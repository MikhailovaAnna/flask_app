FROM python:3
ADD . /web_app
WORKDIR /web_app
RUN pip install -r requirements.txt