FROM python:3 as builder

RUN apt-get update -y && apt-get install -y \
        build-essential \
        default-libmysqlclient-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./requirements.txt
COPY plugin-requirements.txt ./plugin-requirements.txt
RUN pip install \
  -r requirements.txt \
  -r plugin-requirements.txt

FROM python:slim as base

RUN mkdir /opt/kpireport
WORKDIR /opt/kpireport

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

FROM base as dev

RUN apt-get update -y && apt-get install -y \
        netcat \
    && rm -rf /var/lib/apt/lists/*

ADD https://raw.githubusercontent.com/eficode/wait-for/master/wait-for /usr/local/bin/wait-for
RUN chmod +x /usr/local/bin/wait-for

RUN pip install tox

COPY ./dev/entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]

FROM base as release

COPY kpireport .
COPY plugins .
COPY setup.* .

RUN pip install . \
  $(find plugins -mindepth 1 -maxdepth 1 -type d)
