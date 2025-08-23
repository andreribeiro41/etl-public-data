import pandas as pd

df = pd.read_csv("data/processed/daily_weather.csv")
print(df.head())

# import pandas as pd, sqlalchemy as sa
# eng = sa.create_engine("sqlite:///data/weather.db")
# print(pd.read_sql("select * from weather_daily limit 5", eng))

# /home/andreborges/Documentos/etl-open-meteo-template/src/etl/exploratoria.py
# /home/andreborges/Documentos/etl-open-meteo-template/data/processed/daily_weather.csv
