FROM python:3.7-alpine AS build
RUN apk update \
    && apk add git gcc g++ musl-dev libffi-dev openssl-dev make tzdata \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt \
    && mkdir -p /install/lib/python3.7/site-packages \
    && cp -rp /usr/local/lib/python3.7/site-packages /install/lib/python3.7

FROM python:3.7-alpine
COPY --from=build /install/lib /usr/local/lib
COPY --from=build /etc/localtime /etc/localtime
COPY --from=build /etc/timezone /etc/timezone
RUN apk update\
    && apk add libstdc++
WORKDIR /app
COPY . /app
CMD ["python","index.py"]