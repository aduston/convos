FROM ubuntu:latest
RUN apt-get update && apt-get install -y ffmpeg python3-pip python3.12-venv
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN /opt/venv/bin/pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["/opt/venv/bin/python", "main.py"]
