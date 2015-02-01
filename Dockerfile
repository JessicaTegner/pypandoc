# --------------------------------------------------------------------------
# This is a Dockerfile to build an Ubuntu 14.04 Docker image with pypandoc
# and pandoc
#
# Use a command like:
#     docker build -t <user>/pypandoc .
# --------------------------------------------------------------------------

FROM  orchardup/python:2.7
MAINTAINER  Marc Abramowitz <marc@marc-abramowitz.com> (@msabramo)

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL C

RUN apt-get update && apt-get install -y pandoc ipython
ADD . pypandoc
WORKDIR pypandoc
RUN python setup.py install

RUN mkdir -p /source
WORKDIR /source

CMD ["/usr/bin/python"]
