#!/bin/sh
celery -A app.celery_app beat --loglevel=info
