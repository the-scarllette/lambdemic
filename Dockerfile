FROM tensorflow\tensorflow:2.4.1-gpu
USER re412
WORKDIR /app
RUN pip install matplotlib