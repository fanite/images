FROM python:3-slim AS build-env

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        rclone \
        tar

COPY multi_libstrm.py /app/libstrm.py
COPY requirements.txt /app/requirements.txt
COPY profile.json /app/profile.json
COPY logger.py /app/logger.py
COPY monitor.py /app/monitor.py
COPY utils.py /app/utils.py

WORKDIR /app

FROM distroless/python3:latest

COPY --from=build-env /app /app
COPY --from=build-env /usr/bin/rclone /usr/bin/rclone
COPY --from=build-env /usr/bin/tar /usr/bin/tar

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3"]

WORKDIR /app/

ENTRYPOINT ["libstrm.py"]