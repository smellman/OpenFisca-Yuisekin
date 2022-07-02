FROM python:3.8-bullseye
USER root

RUN apt update
RUN apt install -y vim htop jq curl

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

WORKDIR /app
COPY . /app

RUN useradd -m user
USER user

EXPOSE 5000

CMD ["bash"]
