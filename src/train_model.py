import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
import joblib

df = pd.read_csv("data/processed.csv")

X = df.drop(columns=["price_bid_local"])
y_price = df["price_bid_local"]
y_accept = df["price_bid_local"]

X_classifier = df.drop(columns=["price_bid_local"])
y_classifier = y_accept

X_train, X_test, y_train_p, y_test_p = train_test_split(X, y_price, test_size=0.2, random_state=42)
Xc_train, Xc_test, yc_train, yc_test = train_test_split(X_classifier, y_classifier, test_size=0.2, random_state=42)

regressor = GradientBoostingRegressor()
regressor.fit(X_train, y_train_p)

classifier = GradientBoostingClassifier()
classifier.fit(Xc_train, yc_train)

joblib.dump(regressor, "models/regressor_price.pkl")
joblib.dump(classifier, "models/classifier_accept.pkl")

joblib.dump(list(X_train.columns), "models/feature_columns_regressor.pkl")
joblib.dump(list(Xc_train.columns), "models/feature_columns_classifier.pkl")

print("Модели успешно обучены и сохранены")