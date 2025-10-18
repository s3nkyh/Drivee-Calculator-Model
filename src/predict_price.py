import pandas as pd
import joblib
import datetime

MODEL_PATH = "models/fair_price_model.pkl"
model = joblib.load(MODEL_PATH)
print("Модель успешно загружена")

def compute_fair_price(
    distance_in_meters,
    duration_in_seconds,
    pickup_in_meters,
    pickup_in_seconds,
    driver_rating,
    order_timestamp=None,
    driver_experience_days=100,
    weather="ясно",
    traffic_level="средний",
    is_holiday=False,
    passengers=1
):
    """
    Рассчитывает справедливую цену поездки с учётом коэффициентов.
    """

    if order_timestamp is None:
        order_timestamp = datetime.datetime.now()

    order_hour = order_timestamp.hour
    order_wday = order_timestamp.weekday()
    order_month = order_timestamp.month

    data = pd.DataFrame([{
        "distance_in_meters": distance_in_meters,
        "duration_in_seconds": duration_in_seconds,
        "pickup_in_meters": pickup_in_meters,
        "pickup_in_seconds": pickup_in_seconds,
        "driver_rating": driver_rating,
        "order_hour": order_hour,
        "order_wday": order_wday,
        "order_month": order_month,
        "driver_experience_days": driver_experience_days
    }])

    base_price = model.predict(data)[0]

    weather_coef = 1.0
    if weather.lower() in ["дождь", "снег", "гроза"]:
        weather_coef = 1.15  # +15%
    elif weather.lower() in ["шторм", "сильный снегопад"]:
        weather_coef = 1.3   # +30%

    traffic_coef = {
        "низкий": 0.95,
        "средний": 1.0,
        "высокий": 1.2,
        "очень высокий": 1.35
    }.get(traffic_level.lower(), 1.0)

    holiday_coef = 1.15 if is_holiday else 1.0
    passengers_coef = 1.0 + (0.05 * max(0, passengers - 1))

    fair_price = base_price * weather_coef * traffic_coef * holiday_coef * passengers_coef
    return round(fair_price, 2)

if __name__ == "__main__":
    price = compute_fair_price(
        distance_in_meters=7500,
        duration_in_seconds=1200,
        pickup_in_meters=300,
        pickup_in_seconds=180,
        driver_rating=4.8,
        weather="дождь",
        traffic_level="высокий",
        is_holiday=True,
        passengers=2
    )
    print(f"Справедливая цена поездки: {price} руб.")