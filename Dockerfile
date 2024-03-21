FROM python:3-alpine

WORKDIR /var/lib/font2svg

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
