FROM python:3.14-slim

WORKDIR /backend

COPY requirements.txt ./requirements.txt

RUN python -m pip install \
    --no-cache-dir \
    -r requirements.txt

COPY backend/ ./backend/

WORKDIR /backend/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]