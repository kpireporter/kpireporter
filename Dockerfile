FROM python:3 as builder

RUN apt-get update -y && apt-get install -y \
        build-essential \
        default-libmysqlclient-dev \
        netcat \
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

FROM python:3 as dev

ADD https://raw.githubusercontent.com/eficode/wait-for/master/wait-for /usr/local/bin/wait-for
RUN chmod +x /usr/local/bin/wait-for

RUN mkdir /opt/kpireport
WORKDIR /opt/kpireport

COPY --from=builder /opt/venv /opt/kpireport/venv
ENV PATH="/opt/kpireport/venv/bin:$PATH"

FROM dev as release

COPY kpireport .
COPY plugins .
COPY setup.* .

ARG pip_flags=
RUN pip install \
      ${pip_flags} . \
      ${pip_flags} plugins/jenkins \
      ${pip_flags} plugins/mysql
