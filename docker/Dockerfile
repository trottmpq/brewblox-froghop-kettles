FROM python:3.7 as base

COPY docker/dist /app/dist
COPY docker/requirements.txt /app/requirements.txt

ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
ENV PIP_FIND_LINKS=/wheeley
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN pip3 install wheel \
    && pip3 wheel --wheel-dir=/wheeley -r /app/requirements.txt \
    && pip3 wheel --wheel-dir=/wheeley /app/dist/*

FROM python:3.7-slim
EXPOSE 5000
WORKDIR /app

ARG service_info=UNKNOWN
ENV SERVICE_INFO=${service_info}

COPY --from=base /wheeley /wheeley

RUN pip3 install --no-index --find-links=/wheeley brewblox-froghop-kettles \
    && rm -rf /wheeley \
    && pip3 freeze

ENTRYPOINT ["python3", "-m", "brewblox_froghop_kettles"]
