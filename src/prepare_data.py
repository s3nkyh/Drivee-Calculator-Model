import pandas as pd
from datetime import datetime

df = pd.read_csv("data/train.csv")

df["order_timestamp"] = pd.to_datetime(df["order_timestamp"])
df["driver_reg_date"] = pd.to_datetime(df["driver_reg_date"])

df["order_hour"] = df["order_timestamp"].dt.hour
df["order_wday"] = df["order_timestamp"].dt.weekday
df["order_month"] = df["order_timestamp"].dt.month
df["driver_experience_days"] = (df["order_timestamp"] - df["driver_reg_date"]).dt.days

df["driver_rating"] = df["driver_rating"].fillna(df["driver_rating"].median())

cols = [
    "distance_in_meters", "duration_in_seconds",
    "pickup_in_meters", "pickup_in_seconds",
    "driver_rating","order_hour",
    "order_wday", "order_month",
    "driver_experience_days",
    "price_start_local", "price_bid_local", "is_done"
]
df = df[cols]

df.to_csv("data/processed.csv", index=False)
print("Данные успешно подготовлены и сохранены в data/processed.csv")
