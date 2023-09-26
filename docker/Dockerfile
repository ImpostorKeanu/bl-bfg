FROM python:3.9.2
COPY . /opt/bl-bfg
RUN pip3 install /opt/bl-bfg/
WORKDIR /bfg
ENTRYPOINT bfg yaml
