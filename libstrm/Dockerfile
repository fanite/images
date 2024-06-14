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

WORKDIR /app/

CMD ["python"]
ENTRYPOINT ["libstrm.py"]