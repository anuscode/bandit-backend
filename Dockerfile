FROM python:3.10.8-slim-buster

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

COPY ../.. /opt/bandit-backend
WORKDIR /opt/bandit-backend

EXPOSE 80 50051

CMD ["python", "main.py"]
