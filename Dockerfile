FROM python:3.10

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app/main.py /code/app/main.py
COPY ./app/IATA_Codes.db /code/IATA_Codes.db



CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

