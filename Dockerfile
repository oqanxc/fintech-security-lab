FROM python:3.11-slim-bookworm AS builder

LABEL maintainer="DevSecOps Engineering"
WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpcre2-8-0 && \
    apt-get upgrade -y libpcre2-8-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" wheel && \
    pip install --no-cache-dir --target=/install -r requirements.txt && \
    pip install --no-cache-dir --target=/install --upgrade \
        "msgpack>=1.2.1" "urllib3>=2.8.0"


FROM python:3.11-slim-bookworm
WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpcre2-8-0 && \
    apt-get upgrade -y libpcre2-8-0 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local/lib/python3.11/site-packages
COPY . .


RUN rm -rf /usr/local/lib/python3.11/site-packages/pip* \
           /usr/local/lib/python3.11/site-packages/setuptools* \
           /usr/local/bin/pip* \
           /usr/local/bin/easy_install* && \
    useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser
EXPOSE 5000
CMD ["python", "app.py"]