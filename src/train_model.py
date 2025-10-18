import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import joblib
import os

DATA_PATH = "data/processed.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "fair_price_model.pkl")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Файл: {DATA_PATH} не найден! Запустите prepare_data.py")

df = pd.read_csv(DATA_PATH)
print("Загружено строк:", len(df))

target = "price_bid_local"

features = [
    "distance_in_meters",
    "duration_in_seconds",
    "pickup_in_meters",
    "pickup_in_seconds",
    "driver_rating",
    "order_hour",
    "order_wday",
    "order_month",
    "driver_experience_days"
]

df = df.dropna(subset=features + [target])

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    random_state=42
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
print(f"Средняя ошибка модели: {mae:.2f} rub.")

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_PATH)
print("Модель сохранена в:", MODEL_PATH)