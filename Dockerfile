FROM python:3-alpine
MAINTAINER Pål Andreassen "pal.andreassen@sesam.io"
COPY ./service /service

RUN apk update

RUN pip install --upgrade pip

RUN apk --update add build-base libffi-dev libressl-dev python-dev py-pip
RUN pip install cryptography

COPY service/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY ./service /service

EXPOSE 5000/tcp

CMD ["python3", "-u", "./service/sharepoint.py"]