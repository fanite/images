FROM alpine:edge as builder
RUN set -ex \
    && apk update \
    && apk add --no-cache --virtual .build-deps alpine-conf sudo git curl libc-dev gcc g++ make
WORKDIR /working
RUN git clone https://github.com/flow2000/lookbusy.git \
    && cd lookbusy \
    && chmod +x ./configure \
    && ./configure \
    && make
RUN apk del .build-deps

FROM alpine:edge
RUN apk add --no-cache speedtest-cli alpine-conf
ENV TZ Asia/Shanghai
RUN /sbin/setup-timezone -z $TZ
COPY --from=builder /working/lookbusy/lookbusy /usr/bin/lookbusy
COPY ./scripts /scripts
RUN chmod +x /scripts/*.sh /usr/bin/lookbusy
USER root
CMD ["/scripts/entrypoint.sh"]
