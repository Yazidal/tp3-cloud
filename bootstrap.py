import os
import time
from botocore.exceptions import ClientError
from sqlalchemy import text

from db import engine
from storage import get_s3, BUCKET


def wait_db():
    for _ in range(30):
        try:
            with engine.connect() as c:
                c.execute(text("SELECT 1"))
            return
        except Exception:
            time.sleep(2)
    raise SystemExit("PostgreSQL injoignable")


def ensure_bucket():
    s3 = get_s3()
    for _ in range(30):
        try:
            s3.head_bucket(Bucket=BUCKET)
            return                                   # existe déjà
        except ClientError as e:
            code = str(e.response["Error"]["Code"])
            if code in ("404", "NoSuchBucket", "NotFound"):
                create_bucket(s3)
                return
            time.sleep(2)
        except Exception:
            time.sleep(2)                            # gateway pas encore prête
    raise SystemExit("S3 injoignable")


def create_bucket(s3):
    """Hors us-east-1, AWS exige une LocationConstraint explicite."""
    region = os.getenv("S3_REGION", "us-east-1")
    if region != "us-east-1":
        try:
            s3.create_bucket(
                Bucket=BUCKET,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
            return
        except ClientError:
            pass                                     # backend qui l'ignore
    s3.create_bucket(Bucket=BUCKET)


if __name__ == "__main__":
    wait_db()
    with engine.begin() as c:
        c.execute(text(
            "CREATE TABLE IF NOT EXISTS predictions ("
            "id SERIAL PRIMARY KEY, features TEXT, predicted INTEGER)"
        ))
        c.execute(text(
            "CREATE TABLE IF NOT EXISTS datasets ("
            "id SERIAL PRIMARY KEY, name TEXT, path TEXT)"
        ))
    ensure_bucket()
    print("bootstrap OK : schéma + bucket")