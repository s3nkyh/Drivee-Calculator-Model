import os
import pandas as pd
from datetime import datetime
from src.recommend_logic import recommend_optimal_price

def generate_predictions(input_file="data/test.csv", output_file="data/predictions.csv"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, input_file)
    output_path = os.path.join(base_dir, output_file)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    df = pd.read_csv(input_path)
    predictions = []

    for _, row in df.iterrows():
        try:
            data = row.to_dict()

            reg_date = row.get("driver_reg_date", None)
            if pd.notna(reg_date):
                reg_date = datetime.strptime(reg_date, "%Y-%m-%d")
                data["driver_experience_days"] = (datetime(2020, 9, 30) - reg_date).days  # ориентировочная дата поездки
            else:
                data["driver_experience_days"] = 0

            data.setdefault("has_pet", False)
            data.setdefault("has_baggage", False)
            data.setdefault("urgent", False)
            data.setdefault("traffic_jam", False)
            data.setdefault("weather", "clear")
            data.setdefault("holiday", False)
            data.setdefault("temperature", 15)
            data.setdefault("season", "autumn")
            data.setdefault("passengers", 1)

            result = recommend_optimal_price(data)
            optimal = result.get("optimal_price", None)
            predictions.append(optimal)
        except Exception as e:
            print(f"Ошибка на строке: {e}")
            predictions.append(None)

    pd.DataFrame({"is_done": predictions}).to_csv(output_path, index=False)
    print(f"Файл {output_file} успешно создан в {output_path}")

if __name__ == "__main__":
    generate_predictions()