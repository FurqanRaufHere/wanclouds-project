import requests
from app.celery_app import celery_app
from app.db.database import get_db
from app.models.car_make import get_or_create_make
from app.models.car_model import get_or_create_model
from app.models.car_year import get_or_create_year
from app.models.cars import Car
from app.core.config import BACK4APP_APP_ID, BACK4APP_MASTER_KEY

HEADERS = {
    "X-Parse-Application-Id": BACK4APP_APP_ID,
    "X-Parse-Master-Key": BACK4APP_MASTER_KEY,
}

BASE_URL = "https://parseapi.back4app.com/classes/Car_Model_List"

REQUEST_TIMEOUT_SECONDS = 30


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

            # Always time out: without one, a hung response holds this worker
            # process open indefinitely.
            response = requests.get(
                BASE_URL, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT_SECONDS
            )

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

            new_cars = []
            for item in new_items:
                make_name = item.get("Make", "")
                model_name = item.get("Model", "")
                year_value = item.get("Year")

                # Resolve the make -> model -> year hierarchy top down.
                make = get_or_create_make(db, make_name)
                model = get_or_create_model(db, make.id, model_name)
                year_id = None
                if year_value is not None:
                    year_id = get_or_create_year(db, model.id, year_value).id

                new_cars.append(
                    Car(
                        make_id=make.id,
                        model_id=model.id,
                        category=item.get("Category", ""),
                        year_id=year_id,
                        object_id=item.get("objectId", ""),
                    )
                )

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
