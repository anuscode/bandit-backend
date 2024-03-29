FROM python:3.10.11-slim-buster

ARG GITHUB_TOKEN
RUN echo $GITHUB_TOKEN

RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN git config --global url."https://${GITHUB_TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com/"

RUN apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN GRPC_HEALTH_PROBE_VERSION=v0.3.0 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64
RUN chmod +x /bin/grpc_health_probe

# 'llist' package in requirements.txt requires the gcc module.
# otherwise install will be failed.
RUN apt-get -y update
RUN apt-get -y install gcc

COPY requirements.txt /opt/bandit-backend/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /opt/bandit-backend/requirements.txt

COPY . /opt/bandit-backend
WORKDIR /opt/bandit-backend

RUN pip install -r requirements.txt
# protobuf issue force to downgrade
RUN pip install 'protobuf<=3.20.1' --force-reinstall
EXPOSE 80 50051

CMD ["python", "main.py"]
