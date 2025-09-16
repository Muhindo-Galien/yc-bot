FROM python:3.10-slim

WORKDIR /app

# Install minimal build dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]