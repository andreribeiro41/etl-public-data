import pandas as pd
from src.etl.run_all import transform_hourly, aggregate_daily

def test_transform_and_aggregate():
    df = pd.DataFrame({
        "time": pd.date_range("2024-01-01", periods=5, freq="H"),
        "temperature_2m": [20,21,22,23,24],
        "relativehumidity_2m": [70,71,72,73,74],
        "precipitation": [0,0.1,0,0.2,0],
        "city": ["sao_paulo"]*5
    })
    h = transform_hourly(df)
    d = aggregate_daily(h)
    assert round(float(d.loc[0,"temp_avg"]),2) == 22.00
