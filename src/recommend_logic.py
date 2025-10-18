import pandas as pd
import numpy as np
import datetime
import joblib

regressor = joblib.load("models/regressor_price.pkl")
classifier = joblib.load("models/classifier_accept.pkl")

regressor_features = joblib.load("models/feature_columns_regressor.pkl")
classifier_features = joblib.load("models/feature_columns_classifier.pkl")

def compute_fair_price(data):
    now = datetime.datetime.now()
    df = pd.DataFrame([{
        "distance_in_meters": data["distance_in_meters"],
        "duration_in_seconds": data["duration_in_seconds"],
        "pickup_in_meters": data["pickup_in_meters"],
        "pickup_in_seconds": data["pickup_in_seconds"],
        "driver_rating": data["driver_rating"],
        "driver_experience_days": data["driver_experience_days"],
        "order_hour": now.hour,
        "order_wday": now.weekday(),
        "order_month": now.month,
        "price_start_local": data["price_start_local"]
    }])
    df = df[regressor_features]
    base_price = regressor.predict(df)[0]
    return round(base_price, 2)


def recommend_optimal_price(data):
    base_price = compute_fair_price(data)

    traffic_coef = 1.15 if data.get("traffic_jam", False) else 1.0
    urgent_coef = 1.25 if data.get("urgent", False) else 1.0
    pet_fee = 30 if data.get("has_pet", False) else 0
    baggage_fee = 20 if data.get("has_baggage", False) else 0

    final_base = base_price * traffic_coef * urgent_coef + pet_fee + baggage_fee
    prices = np.linspace(final_base * 0.9, final_base * 1.3, 20)
    results = []

    now = datetime.datetime.now()

    for price in prices:
        row_dict = {
            "distance_in_meters": data["distance_in_meters"],
            "duration_in_seconds": data["duration_in_seconds"],
            "pickup_in_meters": data["pickup_in_meters"],
            "pickup_in_seconds": data["pickup_in_seconds"],
            "driver_rating": data["driver_rating"],
            "driver_experience_days": data["driver_experience_days"],
            "order_hour": now.hour,
            "order_wday": now.weekday(),
            "order_month": now.month,
            "price_start_local": data["price_start_local"],
        }

        if "price_bid_local" in classifier_features:
            row_dict["price_bid_local"] = price

        row = pd.DataFrame([row_dict])
        row = row[classifier_features]
        prob = classifier.predict_proba(row)[0, 1]
        expected_income = price * prob
        results.append((price, prob, expected_income))

    df_res = pd.DataFrame(results, columns=["price", "prob", "expected"])
    best_row = df_res.loc[df_res["expected"].idxmax()]
    safe_candidates = df_res[df_res["prob"] >= 0.8]
    safe_row = safe_candidates.iloc[0] if not safe_candidates.empty else df_res.loc[df_res["prob"].idxmax()]
    risky_candidates = df_res[df_res["prob"] < 0.5]
    risky_row = risky_candidates.iloc[-1] if not risky_candidates.empty else df_res.iloc[-1]

    return {
        "safe_price": round(safe_row["price"], 2),
        "optimal_price": round(best_row["price"], 2),
        "risky_price": round(risky_row["price"], 2),
        "expected_income": round(best_row["expected"], 2)
    }
