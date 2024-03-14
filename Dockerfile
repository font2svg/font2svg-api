FROM python:3-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src /app/src

EXPOSE 80

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
