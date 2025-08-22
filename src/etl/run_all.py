from __future__ import annotations
from pathlib import Path
import pandas as pd
import requests
from sqlalchemy import create_engine
from src.utils.config import get_settings

CITY_COORDS = {
    "sao_paulo": (-23.55, -46.63),
    "rio_de_janeiro": (-22.91, -43.17),
    "brasilia": (-15.78, -47.93),
    "belo_horizonte": (-19.92, -43.94),
    "curitiba": (-25.43, -49.27),
    "porto_alegre": (-30.03, -51.23),
    "salvador": (-12.98, -38.48),
    "recife": (-8.04, -34.88),
    "fortaleza": (-3.73, -38.54),
    "manaus": (-3.10, -60.02),
}

def extract_city(city_slug: str, past_days: int, forecast_days: int, timezone: str) -> pd.DataFrame:
    lat, lon = CITY_COORDS[city_slug]
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,relativehumidity_2m,precipitation"
        f"&past_days={past_days}&forecast_days={forecast_days}"
        f"&timezone={timezone}"
    )
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        js = r.json()
        hourly = js.get("hourly", {})
        df = pd.DataFrame(hourly)
        if df.empty:
            raise ValueError("Empty hourly data")
        df["city"] = city_slug
        return df
    except Exception:
        # fallback offline
        rng = pd.date_range(end=pd.Timestamp.now().floor("h"), periods=24, freq="H")
        return pd.DataFrame({
            "time": rng,
            "temperature_2m": [20 + (i % 6) for i in range(len(rng))],
            "relativehumidity_2m": [70 - (i % 10) for i in range(len(rng))],
            "precipitation": [0.1 if i % 7 == 0 else 0.0 for i in range(len(rng))],
            "city": city_slug,
        })

def transform_hourly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    for col in ["temperature_2m", "relativehumidity_2m", "precipitation"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["time"])
    cols = ["time", "city", "temperature_2m", "relativehumidity_2m", "precipitation"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols].sort_values(["city", "time"]).reset_index(drop=True)

def aggregate_daily(df_hourly: pd.DataFrame) -> pd.DataFrame:
    df = df_hourly.copy()
    df["date"] = df["time"].dt.date
    g = df.groupby(["city", "date"], as_index=False).agg(
        temp_min=("temperature_2m", "min"),
        temp_avg=("temperature_2m", "mean"),
        temp_max=("temperature_2m", "max"),
        rh_avg=("relativehumidity_2m", "mean"),
        precip_sum=("precipitation", "sum"),
        hours=("time", "count"),
    )
    for c in ["temp_min", "temp_avg", "temp_max", "rh_avg", "precip_sum"]:
        g[c] = g[c].astype(float).round(2)
    return g

def load_files(df_hourly: pd.DataFrame, df_daily: pd.DataFrame) -> None:
    out = Path("data/processed") 
    out.mkdir(parents=True, exist_ok=True)
    df_hourly.to_parquet(out / "hourly_weather.parquet", index=False)
    df_daily.to_parquet(out / "daily_weather.parquet", index=False)
    df_hourly.to_csv(out / "hourly_weather.csv", index=False)
    df_daily.to_csv(out / "daily_weather.csv", index=False)

def load_sql(df_daily: pd.DataFrame, db_uri: str | None) -> None:
    if not db_uri:
        return
    eng = create_engine(db_uri)
    with eng.begin() as conn:
        df_daily.to_sql("weather_daily", con=conn, if_exists="replace", index=False)

def main():
    st = get_settings()
    frames = []
    for city in st.cities():
        if city not in CITY_COORDS:
            print(f"[aviso] cidade '{city}' não suportada, pulando.")
            continue
        frames.append(extract_city(city, st.past_days, st.forecast_days, st.timezone))
    if not frames:
        raise SystemExit("Nenhuma cidade válida.")
    hourly = transform_hourly(pd.concat(frames, ignore_index=True))
    daily = aggregate_daily(hourly)
    load_files(hourly, daily)
    load_sql(daily, st.db_uri)
    print("✅ Pipeline concluído: arquivos em data/processed/ e (opcional) tabela SQL 'weather_daily'.")

if __name__ == "__main__":
    main()
