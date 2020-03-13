#Taken from https://runnable.com/docker/python/dockerize-your-flask-application
FROM ubuntu:20.04

MAINTAINER Shubham Mishra "donofsuri@gmail.com"

RUN touch /etc/apt/apt.conf.d/proxy.conf

#RUN echo 'Acquire {\
#    HTTP::proxy "http://172.16.2.30:8080";\
#    HTTPS::proxy "http://172.16.2.30:8080";\
#    }' > /etc/apt/apt.conf.d/proxy.conf

RUN apt-get update -y && \
    apt-get install -y python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8000

ENTRYPOINT [ "gunicorn" ]

CMD [ "app.app:app" ]
