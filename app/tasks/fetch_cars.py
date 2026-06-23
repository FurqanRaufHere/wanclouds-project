import requests
from sqlalchemy.exc import IntegrityError
from app.celery_app import celery_app
from app.db.database import get_db_session
from app.models.cars import Car
from app.core.config import BACK4APP_APP_ID, BACK4APP_MASTER_KEY

HEADERS = {
    "X-Parse-Application-Id": BACK4APP_APP_ID,
    "X-Parse-Master-Key": BACK4APP_MASTER_KEY,
}

BASE_URL = "https://parseapi.back4app.com/classes/Car_Model_List"


@celery_app.task(name="fetch_cars")
def fetch_cars_task():
    total_saved = 0
    total_skipped = 0
    skip = 0
    limit = 100

    for db in get_db_session():
        while True:
            params = {
                "limit": limit,
                "skip": skip,
                "keys": "Make,Model,Category,Year"
            }

            response = requests.get(BASE_URL, headers=HEADERS, params=params)

            if response.status_code != 200:
                break

            results = response.json().get("results", [])

            if not results:
                break

            for item in results:
                existing = db.query(Car).filter(
                    Car.object_id == item.get("objectId")
                ).first()

                if existing:
                    total_skipped += 1
                    continue

                car = Car(
                    make=item.get("Make", ""),
                    model=item.get("Model", ""),
                    category=item.get("Category", ""),
                    year=item.get("Year"),
                    object_id=item.get("objectId", "")
                )
                db.add(car)
                total_saved += 1

            db.commit()

            if len(results) < limit:
                break

            skip += limit

    return {
        "status": "completed",
        "total_saved": total_saved,
        "total_skipped": total_skipped
    }
