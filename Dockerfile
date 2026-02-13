FROM ubuntu:20.04  

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt 

COPY . .

EXPOSE 80

CMD ["python3", "app.py"]