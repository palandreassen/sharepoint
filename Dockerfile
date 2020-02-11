FROM python:3.6-alpine
MAINTAINER Pål Andreassen "pal.andreassen@sesam.io"
COPY ./service /service

RUN apk update
RUN apk add python-dev libxml2-dev libxslt-dev py-lxml musl-dev openssl-dev libffi-dev gcc

RUN pip install --upgrade pip

RUN pip install -r /service/requirements.txt

EXPOSE 5000/tcp

CMD ["python3", "-u", "./service/sharepoint.py"]
