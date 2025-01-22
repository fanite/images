FROM alpine:edge
ENV TZ Asia/Shanghai
RUN apk update && apk add --no-cache \
    alpine-conf \
    zip \
    unzip \
    tar \
    mysql-client \
    rclone \
    kubectl \
    mariadb-connector-c-dev
RUN setup-timezone -z $TZ
RUN mkdir -p /root/.config/rclone/
RUN mkdir -p /workspace/scripts
COPY ./scripts/* /workspace/scripts/
RUN chmod +x /workspace/scripts/*
WORKDIR /workspace
ENTRYPOINT ["/workspace/scripts/mysql.sh"]
