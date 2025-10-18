from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import datetime

MODEL_PATH = r"C:\Users\olkin\PycharmProjects\PythonProject\models\fair_price_model.pkl"
model = joblib.load(MODEL_PATH)
print("Модель загружена успешно")

app = FastAPI(title="Fair Taxi Price API")

class RideRequest(BaseModel):
    distance_in_meters: float
    duration_in_seconds: float
    pickup_in_meters: float
    pickup_in_seconds: float
    driver_rating: float
    driver_experience_days: int = 100
    weather: str = "ясно"
    traffic_level: str = "средний"
    is_holiday: bool = False
    passengers: int = 1

def compute_fair_price(data: RideRequest):
    now = datetime.datetime.now()
    order_hour = now.hour
    order_wday = now.weekday()
    order_month = now.month

    df = pd.DataFrame([{
        "distance_in_meters": data.distance_in_meters,
        "duration_in_seconds": data.duration_in_seconds,
        "pickup_in_meters": data.pickup_in_meters,
        "pickup_in_seconds": data.pickup_in_seconds,
        "driver_rating": data.driver_rating,
        "order_hour": order_hour,
        "order_wday": order_wday,
        "order_month": order_month,
        "driver_experience_days": data.driver_experience_days
    }])

    base_price = model.predict(df)[0]

    weather_coef = 1.0
    if data.weather.lower() in ["дождь", "снег", "гроза"]:
        weather_coef = 1.15
    elif data.weather.lower() in ["шторм", "сильный снегопад"]:
        weather_coef = 1.3

    traffic_coef = {
        "низкий": 0.95,
        "средний": 1.0,
        "высокий": 1.2,
        "очень высокий": 1.35
    }.get(data.traffic_level.lower(), 1.0)

    holiday_coef = 1.15 if data.is_holiday else 1.0
    passengers_coef = 1.0 + (0.05 * max(0, data.passengers - 1))

    fair_price = base_price * weather_coef * traffic_coef * holiday_coef * passengers_coef
    return round(fair_price, 2)

@app.post("/predict")
def predict_price(request: RideRequest):
    fair_price = compute_fair_price(request)
    return {
        "fair_price": fair_price,
        "currency": "RUB",
        "weather": request.weather,
        "traffic": request.traffic_level,
        "is_holiday": request.is_holiday
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api_server:app", host="0.0.0.0", port=8000, reload=True)