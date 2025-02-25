FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get update

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code/