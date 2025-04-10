FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install waitress

EXPOSE 8080

CMD ["python", "run_server.py"]
