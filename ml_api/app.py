from fastapi import FastAPI, Query
from predict import predict_pandemic

app = FastAPI(title="Pandemic Prediction API")


@app.get("/predict")
def get_prediction(
    country: str = Query(..., description="Nom du pays"),
    virus: str = Query(..., description="Nom du virus"),
    date_start: str = Query(...,
                            description="Date de début au format YYYY-MM-DD"),
    date_end: str = Query(..., description="Date de fin au format YYYY-MM-DD")
):
    """
    Endpoint principal pour obtenir les prédictions.
    """
    result = predict_pandemic(country, virus, date_start, date_end)
    return result
