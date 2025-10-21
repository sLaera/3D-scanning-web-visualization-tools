# Dockerfile stages
# Stage 1: Base image with Node.js and essential tools, later extended for Python setup
# Stage 2: Temporary Python image to install dependencies, later copied into base
# Stage 3: Extends base, adds Python environment and mesh reconstruction files
# Stage 4: Installs system libraries and builds Poisson reconstruction


# Stage 1: Base image with Node.js and apt-get
FROM node:22 AS base

RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    libgl1

#_________ Mesh difference python__________
# Python libs installation
FROM python:3.11-slim AS python-deps

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1

RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc
COPY MeshDifferenceVisualization/PythonPreprocessing .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install
# Move Python installation to base image
FROM base AS mesh-reconstruction

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
# recreate broken simlink
RUN ln -sf $(which python3) /usr/local/bin/python

COPY MeshDifferenceVisualization/PythonPreprocessing  ./app/externals/mesh-difference
COPY RemeshingTool  ./app/externals/reconstruction

# ______ Poisson recon__________
FROM mesh-reconstruction
# Library installation
RUN apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libboost-dev \
    libboost-system-dev \
    make

WORKDIR /app/externals/reconstruction/PoissonRecon
#Building
# change `-j 3` base on the number of available threads. This could take up to 30 min
RUN make poissonrecon -j 3
#
#______________________________