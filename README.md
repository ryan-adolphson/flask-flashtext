# Flasktext API

Parse text and find matching terms

## Steps to run service

- Step 1: `docker build -t flashtext-api .`

- Step 2: `docker run -e API_KEYS=my-secret-key -p 8000:8000 flashtext-api`
