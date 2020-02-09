FROM "python:3.8"

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt && pip3 install gunicorn

CMD ["gunicorn", "-b", "0.0.0.0:8080", "dispatch/__init__"]
