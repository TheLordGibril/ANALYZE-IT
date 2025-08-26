from fastapi import FastAPI, Query
from predict import predict_pandemic
from sqlalchemy import create_engine, Table, MetaData, select
from config import config

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


@app.get("/countries")
def get_countries():
    """
    Retourne la liste des pays disponibles.
    """
    engine = create_engine(config.get_database_url())
    meta = MetaData()
    pays = Table('Pays', meta, autoload_with=engine)
    with engine.connect() as conn:
        result = conn.execute(select(pays.c.nom_pays)).fetchall()
        countries = [row[0] for row in result]
    return {"countries": countries}


@app.get("/viruses")
def get_viruses():
    """
    Retourne la liste des virus disponibles.
    """
    engine = create_engine(config.get_database_url())
    meta = MetaData()
    virus = Table('Virus', meta, autoload_with=engine)
    with engine.connect() as conn:
        result = conn.execute(select(virus.c.nom_virus)).fetchall()
        viruses = [row[0] for row in result]
    return {"viruses": viruses}
