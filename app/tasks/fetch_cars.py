import requests
from app.celery_app import celery_app
from app.db.database import get_db
from app.models.car_make import get_or_create_makes
from app.models.car_model import get_or_create_models
from app.models.car_year import get_or_create_years
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

    with get_db() as db:
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

            object_ids = [item.get("objectId") for item in results]
            existing_ids = {
                row.object_id for row in
                db.query(Car.object_id).filter(Car.object_id.in_(object_ids)).all()
            }

            new_items = [item for item in results if item.get("objectId") not in existing_ids]

            make_ids = get_or_create_makes(db, (item.get("Make", "") for item in new_items))
            model_ids = get_or_create_models(db, (item.get("Model", "") for item in new_items))
            year_ids = get_or_create_years(db, (item.get("Year") for item in new_items))

            new_cars = [
                Car(
                    make_id=make_ids[item.get("Make", "")],
                    model_id=model_ids[item.get("Model", "")],
                    category=item.get("Category", ""),
                    year_id=year_ids.get(item.get("Year")),
                    object_id=item.get("objectId", "")
                )
                for item in new_items
            ]

            db.bulk_save_objects(new_cars)
            db.commit()

            total_saved += len(new_cars)
            total_skipped += len(results) - len(new_cars)

            if len(results) < limit:
                break

            skip += limit

    return {
        "status": "completed",
        "total_saved": total_saved,
        "total_skipped": total_skipped
    }
