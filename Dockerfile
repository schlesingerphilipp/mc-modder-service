FROM python:3.11-slim
WORKDIR /modder_mc_service
RUN pip install poetry
RUN apt-get update && apt-get install -y make
# Add the source
COPY modder_mc_service ./modder_mc_service
COPY poetry.lock ./poetry.lock
COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md
COPY Makefile ./Makefile
COPY .env ./.env
RUN make install