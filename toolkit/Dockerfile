FROM alpine:edge
ENV TZ Asia/Shanghai
RUN apk update && apk add --no-cache \
    alpine-conf \
    unzip \
    tar \
    mysql-client \
    rclone \
    kubectl \
RUN /sbin/setup-timezone -z $TZ
RUN mkdir -p /workspace/scripts
COPY ./scripts/* /workspace/scripts/
RUN chmod +x /workspace/scripts/*
WORKDIR /workspace
ENTRYPOINT ["/workspace/scripts/mysql.sh"]