import socket

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from sqlalchemy import text

from db import engine
from predictor import predict_iris
from storage import get_s3, BUCKET


app = FastAPI(title="CODA Monolith")


class Features(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")           # readiness : PostgreSQL + S3
def ready():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        get_s3().head_bucket(Bucket=BUCKET)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    return {"status": "ready"}

@app.get("/info")
def info():
    return {"hostname": socket.gethostname(),
            "version": os.getenv("APP_VERSION", "1.0.0")}


@app.post("/predict")
def predict(features: Features):
    values = [features.sepal_length, features.sepal_width,
              features.petal_length, features.petal_width]
    predicted = int(predict_iris(values))
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO predictions(features, predicted) VALUES (:f, :p)"),
            {"f": str(values), "p": predicted},
        )
    return {"prediction": predicted, "hostname": socket.gethostname()}


@app.get("/predictions")
def predictions():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, features, predicted FROM predictions ORDER BY id")
        ).fetchall()
    return [{"id": r[0], "features": r[1], "prediction": r[2]} for r in rows]


@app.post("/datasets")
async def upload_dataset(file: UploadFile = File(...)):
    get_s3().upload_fileobj(file.file, BUCKET, file.filename)
    location = f"s3://{BUCKET}/{file.filename}"
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO datasets(name, path) VALUES (:n, :p)"),
            {"n": file.filename, "p": location},
        )
    return {"name": file.filename, "path": location, "hostname": socket.gethostname()}


@app.get("/datasets")
def datasets():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, name, path FROM datasets ORDER BY id")
        ).fetchall()
    return [{"id": r[0], "name": r[1], "path": r[2]} for r in rows]