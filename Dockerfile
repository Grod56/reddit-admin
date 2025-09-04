FROM python:3.11-slim
WORKDIR /usr/src/reddit-admin
COPY botapplicationtools botapplicationtools/
COPY resources resources/
COPY __init__.py .
COPY requirements.txt .
COPY praw.ini .
COPY reddit-admin.py .
ENV DATABASE_URL=$DATABASE_URL
RUN \
    apt-get update && \
    apt-get install -o APT::Keep-Downloaded-Packages=false -y libpq-dev gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y libpq-dev gcc
CMD ["python", "reddit-admin.py", "0"]