FROM python:3.11-slim-bookworm

LABEL maintainer="DevSecOps Engineering"

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y libpcre2-8-0 && \
    apt-get upgrade -y libpcre2-8-0 && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip "setuptools>=78.1.1" wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade "msgpack>=1.2.1" && \
    pip install --no-cache-dir --upgrade --force-reinstall "urllib3>=2.8.0"

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]