import pandas as pd
import numpy as np
import datetime

MAX_DISTANCE = 100000
MAX_PICKUP_DISTANCE = 5000

def clip_features(data):
    """Ограничиваем экстремальные значения признаков."""
    return {
        "distance_in_meters": min(data["distance_in_meters"], MAX_DISTANCE),
        "pickup_in_meters": min(data["pickup_in_meters"], MAX_PICKUP_DISTANCE),
        "driver_rating": data["driver_rating"],
        "driver_experience_days": data["driver_experience_days"],
        "price_start_local": data["price_start_local"],
        "has_pet": data.get("has_pet", False),
        "has_baggage": data.get("has_baggage", False),
        "urgent": data.get("urgent", False),
        "traffic_jam": data.get("traffic_jam", False),
        "weather": data.get("weather", "clear"),
        "holiday": data.get("holiday", False),
        "temperature": data.get("temperature", 20),
        "season": data.get("season", "spring"),
        "passengers": data.get("passengers", 1)
    }

def compute_fair_price(data, avg_speed_kmh=60):
    """Справедливая цена с учётом всех факторов и скидок."""
    data = clip_features(data)

    distance_km = data["distance_in_meters"] / 1000
    pickup_km = data["pickup_in_meters"] / 1000

    duration_min = (distance_km / avg_speed_kmh) * 60
    pickup_min = pickup_km * 5

    base_price = 50 + 15 * distance_km + 5 * duration_min + 10 * pickup_km + pickup_min

    traffic_coef = 1.20 if data["traffic_jam"] else 1.0
    urgent_coef = 1.30 if data["urgent"] else 1.0
    pet_fee = 30 if data["has_pet"] else 0
    baggage_fee = 20 if data["has_baggage"] else 0
    driver_coef = 1 + (data["driver_rating"] - 4.5) * 0.1 + min(data["driver_experience_days"]/1000, 0.2)

    weather_coef = {"clear": 1.0, "rain": 1.15, "snow": 1.25, "storm": 1.35}
    weather_mult = weather_coef.get(data["weather"], 1.0)

    if data["temperature"] < 0:
        temp_coef = 1.15
    elif data["temperature"] > 35:
        temp_coef = 1.10
    else:
        temp_coef = 1.0

    season_coef = {"spring": 1.0, "summer": 1.0, "autumn": 1.05, "winter": 1.10}
    season_mult = season_coef.get(data["season"], 1.0)

    now = datetime.datetime.now()
    hour = now.hour
    time_coef = 1.15 if hour < 6 or hour > 22 else 1.0

    weekday = now.weekday()
    weekday_coef = 1.05 if weekday >= 5 else 1.0

    holiday_coef = 1.25 if data["holiday"] else 1.0

    passenger_fee = 0
    if data["passengers"] > 4:
        passenger_fee = (data["passengers"] - 4) * 15

    fair_price = base_price
    fair_price *= traffic_coef * urgent_coef * driver_coef
    fair_price *= weather_mult * temp_coef * season_mult * time_coef * weekday_coef * holiday_coef
    fair_price += pet_fee + baggage_fee + passenger_fee
    fair_price = round(fair_price, 2)

    discounts = [0.10, 0.15, 0.20]
    discounted_prices = {f"discount_{int(d*100)}": round(fair_price * (1 - d), 2) for d in discounts}

    return {
        "fair_price": fair_price,
        **discounted_prices
    }

def recommend_optimal_price(data, start_price_influence=0.5, avg_speed_kmh=60):
    """Рассчитываем safe, optimal и risky цены с expected_income."""
    data = clip_features(data)
    fair_dict = compute_fair_price(data, avg_speed_kmh)
    fair_price = fair_dict["fair_price"]

    prices = np.linspace(fair_price * 0.7, fair_price * 1.3, 20)
    results = []

    for price in prices:
        prob = max(0.0, 1 - abs(price - fair_price)/fair_price)
        expected_income = price * prob
        results.append((price, prob, expected_income))

    df_res = pd.DataFrame(results, columns=["price", "prob", "expected"])
    best_row = df_res.loc[df_res["expected"].idxmax()]

    safe_candidates = df_res[df_res["prob"] >= 0.8].reset_index(drop=True)
    if not safe_candidates.empty:
        sorted_candidates = safe_candidates.iloc[(safe_candidates["price"] - fair_price).abs().argsort()]
        safe_row = sorted_candidates.iloc[0]
        if safe_row["price"] >= best_row["price"] and len(sorted_candidates) > 1:
            safe_row = sorted_candidates.iloc[1]
    else:
        safe_row = best_row

    risky_candidates = df_res[df_res["price"] <= fair_price].reset_index(drop=True)
    if not risky_candidates.empty:
        risky_row = risky_candidates.iloc[risky_candidates["price"].idxmin()]
    else:
        risky_row = df_res.iloc[0]

    return {
        "safe_price": round(safe_row["price"], 2),
        "optimal_price": round(best_row["price"], 2),
        "risky_price": round(risky_row["price"], 2),
        "expected_income": round(best_row["expected"], 2)
    }
