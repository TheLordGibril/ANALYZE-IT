# app.py
from fastapi import FastAPI, Query
from predict import predict_pandemic

app = FastAPI(title="Pandemic Prediction API")


@app.get("/predict")
def get_prediction(
    country: str = Query(..., description="Nom du pays"),
    virus: str = Query(..., description="Nom du virus"),
    date: str = Query(..., description="Date de départ au format YYYY-MM-DD")
):
    """
    Endpoint principal pour obtenir les prédictions.
    """
    result = predict_pandemic(country, virus, date)
    return result
