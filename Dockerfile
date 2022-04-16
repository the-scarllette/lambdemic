FROM tensorflow/tensorflow:latest-gpu

WORKDIR /app

RUN python3 -m pip install matplotlib
