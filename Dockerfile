# PRODUCTION DOCKERFILE
FROM python:3.9-slim

# install deps as root
COPY ./src/requirements.txt .
RUN pip3  --disable-pip-version-check --no-cache-dir install -r requirements.txt
RUN rm -v requirements.txt

# make the nonroot user
RUN useradd tc -m -s /usr/sbin/nologin

# copy the source code
WORKDIR /home/tc/app
COPY ./src/app .

# fix ownership of stuff inside application folder
RUN chown -R tc:tc .

# run uvicorn as nonroot
USER tc
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000", "--no-server-header", "--workers", "8" ]