from python:3

RUN apt-get update -y && apt-get install -y \
        build-essential \
        default-libmysqlclient-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/* 

RUN mkdir /opt/reportcard
WORKDIR /opt/reportcard

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY reportcard ./reportcard
COPY setup.cfg ./setup.cfg
COPY setup.py ./setup.py

RUN python setup.py install
