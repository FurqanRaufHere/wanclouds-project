import requests
from sqlalchemy.exc import IntegrityError
from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.cars import Car
from app.core.config import BACK4APP_APP_ID, BACK4APP_MASTER_KEY, BACK4APP_BASE_URL

CAR_CLASSES = [
    "Car_Model_List_Toyota",
    "Car_Model_List_Honda",
    "Car_Model_List_Ford",
    "Car_Model_List_BMW",
    "Car_Model_List_Mercedes_Benz",
    "Car_Model_List_Nissan",
    "Car_Model_List_Chevrolet",
    "Car_Model_List_Audi",
]

HEADERS = {
    "X-Parse-Application-Id": BACK4APP_APP_ID,
    "X-Parse-Master-Key": BACK4APP_MASTER_KEY,
}


@celery_app.task(name="fetch_cars")
def fetch_cars_task():
    db = SessionLocal()
    total_saved = 0
    total_skipped = 0

    try:
        for car_class in CAR_CLASSES:
            skip = 0
            limit = 100

            while True:
                url = f"{BACK4APP_BASE_URL}/{car_class}"
                params = {
                    "limit": limit,
                    "skip": skip,
                    "keys": "Make,Model,Category,Year"
                }

                response = requests.get(url, headers=HEADERS, params=params)

                if response.status_code != 200:
                    break

                results = response.json().get("results", [])

                if not results:
                    break

                for item in results:
                    car = Car(
                        make=item.get("Make", ""),
                        model=item.get("Model", ""),
                        category=item.get("Category", ""),
                        year=item.get("Year"),
                        object_id=item.get("objectId", "")
                    )
                    try:
                        db.add(car)
                        db.commit()
                        total_saved += 1
                    except IntegrityError:
                        db.rollback()
                        total_skipped += 1

                if len(results) < limit:
                    break

                skip += limit

    finally:
        db.close()

    return {
        "status": "completed",
        "total_saved": total_saved,
        "total_skipped": total_skipped
    }
