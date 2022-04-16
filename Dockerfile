FROM tensorflow/tensorflow:latest-gpu
USER re412
WORKDIR /app
RUN pip install matplotlib