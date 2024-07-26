FROM python:slim-bookworm AS build

WORKDIR /build_code
COPY ./training .
RUN apt update \
    && apt install -y libgl1 libglib2.0-0 \
    && apt clean \
    && pip install --no-cache-dir --upgrade -r requirements.txt \
    && python3 main.py --preprocess


FROM python:slim-bookworm AS deploy

WORKDIR /deploy_code
COPY ./fastapi .
COPY --from=build /build_code/models /deploy_code/models

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ENTRYPOINT [ "python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0" ]

EXPOSE 8000
