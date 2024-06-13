FROM python:alpine

RUN apk update && apk add --no-cache \
    rclone \
    tar \
    kubectl

COPY . /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade setuptools

WORKDIR /app/

CMD ["python3"]
ENTRYPOINT ["libstrm.py"]