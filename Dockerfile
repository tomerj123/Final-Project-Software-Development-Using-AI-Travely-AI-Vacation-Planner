FROM python:3.10
WORKDIR /app

# Copy the React build from the previous stage
COPY requirements.txt /app/requirements.txt

# Install FastAPI dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app/main.py /app/main.py
COPY ./app/IATA_Codes.db /app/IATA_Codes.db

# Run FastAPI server

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]