# --------------------------------------------------------------------------
# This is a Dockerfile to build a Debian image with pypandoc and pandoc.
#
# Use a command like:
#     docker build -t <user>/pypandoc .
# --------------------------------------------------------------------------

FROM  python:3.12
LABEL author  Jessica Tegner <jessica@jessicategner.com> and pypandoc contributors
# Update apt packages and install pandoc
RUN apt update && apt upgrade -y && apt install pandoc -y
# Update pip
RUN pip install --upgrade pip

# Copy the files to container   
COPY . pypandoc
WORKDIR pypandoc

# Use pip to install the local version of pypandoc using pyproject.toml
RUN pip install .

RUN mkdir -p /source
WORKDIR /source

CMD ["/usr/bin/python"]
