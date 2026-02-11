@echo off
cd C:\Users\n2t\Documents\english_study\backend\
start "Celery Worker" cmd /k celery -A config worker -l info
start "Celery Beat" cmd /k celery -A config beat -l info
