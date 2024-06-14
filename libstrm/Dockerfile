FROM alpine:edge

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-setuptools \
    rclone \
    tar \
    kubectl \
    fuse3

COPY . /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade setuptools

WORKDIR /app/

CMD ["python3"]
ENTRYPOINT ["libstrm.py"]