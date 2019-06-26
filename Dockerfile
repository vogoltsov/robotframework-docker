FROM ubuntu

RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y \
        docker.io \
        docker-compose \
        python3 \
        python3-pip \
 && rm -rf /var/lib/apt/lists/*

ADD . /sources/
RUN cd /sources \
 && python3 /sources/setup.py -q install \
 && rm -rf /sources

ADD docker-entrypoint.sh /
RUN chmod a+x /docker-entrypoint.sh
ENTRYPOINT [ "/docker-entrypoint.sh" ]

CMD [ "bash" ]
