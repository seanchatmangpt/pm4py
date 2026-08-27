FROM elixir:1.18.4-otp-27-slim AS paas-builder

ENV MIX_ENV=prod
WORKDIR /src/paas
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && mix local.hex --force \
    && mix local.rebar --force
COPY paas/mix.exs ./
RUN mix deps.get
COPY paas ./
RUN mix deps.compile && mix compile --warnings-as-errors && mix release

FROM python:3.14-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PM4PY_DATA_ROOT=/app/data \
    PORT=8000

RUN apt-get update && apt-get install -y --no-install-recommends graphviz curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 pm4py \
    && mkdir -p /app/data /src

WORKDIR /src
COPY . .
RUN pip install --no-cache-dir -e .

COPY --from=paas-builder /src/paas/_build/prod/rel/pm4py_paas /opt/pm4py_paas
RUN chown -R pm4py:pm4py /app /opt/pm4py_paas /src
USER pm4py

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 CMD curl -fsS http://localhost:8000/health || exit 1
CMD ["/opt/pm4py_paas/bin/pm4py_paas", "start"]
