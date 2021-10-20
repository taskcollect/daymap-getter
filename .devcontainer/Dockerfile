# https://github.com/microsoft/vscode-dev-containers/tree/v0.187.0/containers/go/.devcontainer/base.Dockerfile

ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}


# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

WORKDIR /root/workspace
COPY ./src/requirements.txt ./src/requirements.txt

# install dependencies from requirements.txt
RUN pip3 --disable-pip-version-check --no-cache-dir install -r ./src/requirements.txt \
    && rm -rf /tmp/pip-tmp