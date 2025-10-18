from fastapi import FastAPI
from pydantic import BaseModel
from src.recommend_logic import recommend_optimal_price, compute_fair_price

app = FastAPI()

class RideRequest(BaseModel):
    distance_in_meters: float
    pickup_in_meters: float
    pickup_in_seconds: float
    driver_rating: float
    driver_experience_days: int
    price_start_local: float
    has_pet: bool = False
    has_baggage: bool = False
    urgent: bool = False
    traffic_jam: bool = False
    weather: str = "clear"
    holiday: bool = False
    temperature: float = 20
    season: str = "spring"
    passengers: int = 1

@app.post("/fair_price")
def get_fair_price(request: RideRequest):
    fair = compute_fair_price(request.dict())
    return {"fair_price": fair}

@app.post("/recommend")
def get_recommendation(request: RideRequest):
    rec = recommend_optimal_price(request.dict())
    return rec
