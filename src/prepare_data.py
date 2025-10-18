import pandas as pd
import os

INPUT_PATH = "data/train.csv"
OUTPUT_PATH = "data/processed.csv"

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"File {INPUT_PATH} not found.")

df = pd.read_csv(INPUT_PATH)
print("Data is uploaded:", df.shape)

print("Columns:", list(df.columns))

df['bargain_happened'] = (df['price_bid_local'] != df['price_start_local']).astype(int)
df['order_timestamp'] = pd.to_datetime(df['order_timestamp'])
df['driver_reg_date'] = pd.to_datetime(df['driver_reg_date'])


df['order_hour'] = df['order_timestamp'].dt.hour
df['order_wday'] = df['order_timestamp'].dt.weekday
df['order_month'] = df['order_timestamp'].dt.month

df['driver_experience_days'] = (df['order_timestamp'] - df['driver_reg_date']).dt.days

top_models = df['carmodel'].value_counts().head(10).index
df['carmodel_top'] = df['carmodel'].where(df['carmodel'].isin(top_models), 'OTHER')

df.to_csv(OUTPUT_PATH, index=False)
print("Готовые данные сохранены в:", OUTPUT_PATH)
