FROM python:3.6
MAINTAINER Pål Andreassen "pal.andreassen@sesam.io"
COPY ./service /service

WORKDIR /service
ADD ./service/requirements.txt /service/requirements.txt
RUN pip install -r requirements.txt

ADD . /service

EXPOSE 5000/tcp

CMD ["python3", "-u", "./service/sharepoint.py"]