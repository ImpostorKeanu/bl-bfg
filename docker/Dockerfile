FROM python:latest
COPY . /opt/bl-bfg
RUN pip3 install /opt/bl-bfg/
WORKDIR /bfg
ENTRYPOINT bfg yaml
