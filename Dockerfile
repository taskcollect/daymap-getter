# PRODUCTION DOCKERFILE

FROM python:3.9-slim

RUN useradd tc -m -s /bin/nologin
USER tc

WORKDIR /home/tc/app

COPY ./src .
RUN pip3  --disable-pip-version-check --no-cache-dir install --user -r requirements.txt

CMD [ "python3", "main.py" ]