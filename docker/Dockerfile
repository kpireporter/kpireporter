ARG python_version=3
FROM python:$python_version as builder

RUN apt-get update -y && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt
COPY plugin-requirements.txt ./plugin-requirements.txt
RUN pip install --upgrade pip wheel
RUN pip install --no-cache-dir \
  -r requirements.txt \
  -r plugin-requirements.txt

FROM python:$python_version as base

# Install wait-for helper script.
RUN apt-get update \
  && apt-get install --no-install-recommends -y netcat \
  && rm -rf /var/lib/apt/lists/*
ADD https://raw.githubusercontent.com/eficode/wait-for/master/wait-for /usr/local/bin/wait-for
RUN chmod +x /usr/local/bin/wait-for

# Install any binaries required by the default set of plugins.
RUN apt-get update && apt-get install -y --no-install-recommends \
      wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /opt/kpireport
WORKDIR /opt/kpireport

# Declare a volume for any additional plugins to
# be mounted in at container runtime.
VOLUME /plugins

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

FROM base as dev

RUN apt-get update && apt-get install -y --no-install-recommends \
        entr silversearcher-ag \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir tox

COPY ./dev/entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]

FROM base as release

COPY kpireport ./kpireport
COPY plugins ./plugins
COPY setup.* ./

# Due to pip not having a dependency resolver[1], we need
# to ensure that any "base" plugins that are used by other
# plugins are installed first; the "static" plugin is the
# first example.
# [1]: https://github.com/pypa/pip/issues/988
RUN pip install --no-cache-dir . plugins/static \
  && find plugins -mindepth 1 -maxdepth 1 -type d \
    -exec pip install --no-cache-dir {} \;

COPY docker/entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]
