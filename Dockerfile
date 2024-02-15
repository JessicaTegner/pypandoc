# --------------------------------------------------------------------------
# This is a Dockerfile to build an Debian 11 (bullseye) image with pypandoc
# and pandoc, uses Python 3.9.
#
# Use a command like:
#     docker build -t <user>/pypandoc .
# --------------------------------------------------------------------------

# Use Python 3.9
FROM  python:3.12
# Not sure if this line needs updating, I think this person no longer works on the project?
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
