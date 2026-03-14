FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/       ./src/
COPY static/    ./static/
COPY templates/ ./templates/
COPY setup.py   .

RUN pip install --no-cache-dir -e .

ENV PYTHONPATH=/app/src
ENV FLASK_APP=mutau_website

EXPOSE 5000

CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--preload", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "mutau_website:create_app()"]