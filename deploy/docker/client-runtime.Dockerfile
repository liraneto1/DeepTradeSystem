# Linux/amd64 I00 profile approved on 2026-11-17; PostgreSQL server is separate.
ARG BASE=python@sha256:c5ba3deef00c7758561a0f03c26f44f10589263d40e732b8748e0d1f38f6dd89
ARG UVBASE=ghcr.io/astral-sh/uv@sha256:9a23023be68b2ed09750ae636228e903a54a05ea56ed03a934d00fe9fbeded4b
FROM ${UVBASE} AS uvtool
FROM ${BASE} AS test
ENV UV_PYTHON_DOWNLOADS=never UV_NO_PROGRESS=1 UV_LINK_MODE=copy SOURCE_DATE_EPOCH=315532800
WORKDIR /workspace
COPY --from=uvtool /uv /usr/local/bin/uv
COPY deploy/docker/client-apk-lock.json deploy/docker/client-apk-lock.json
COPY tools/client_profile/install_apks.py tools/client_profile/install_apks.py
RUN python tools/client_profile/install_apks.py test --archive
COPY . /workspace/
RUN uv sync --locked --only-group build --python /usr/local/bin/python3.12
RUN .venv/bin/python tools/client_profile/build.py
ENV PATH="/workspace/.venv/bin:${PATH}" PSYCOPG_IMPL=c LIVE_ENABLED=false TRADE_SYSTEM_ENVIRONMENT=PAPER
RUN python tools/client_profile/inventory.py /audit/test-inventory

FROM ${BASE} AS runtime
WORKDIR /workspace
COPY deploy/docker/client-apk-lock.json deploy/docker/client-apk-lock.json
COPY tools/client_profile/install_apks.py /tools/install_apks.py
RUN python /tools/install_apks.py runtime
RUN python -m pip uninstall --yes pip && python -c "import ensurepip,pathlib; p=pathlib.Path(ensurepip.__file__).parent/'_bundled'; [f.unlink() for f in p.glob('*.whl')]"
COPY --from=test /opt/runtime /opt/runtime
COPY --from=test /workspace/src /workspace/src
COPY --from=test /workspace/infrastructure /workspace/infrastructure
COPY --from=test /workspace/apps /workspace/apps
COPY tools/client_profile/inventory.py /tools/inventory.py
ENV PATH="/opt/runtime/bin:${PATH}" PSYCOPG_IMPL=c LIVE_ENABLED=false TRADE_SYSTEM_ENVIRONMENT=PAPER
RUN python /tools/inventory.py /audit/runtime-inventory
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "127.0.0.1", "--port", "8000"]
