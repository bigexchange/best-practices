FROM python:3.6.7
RUN apt-get update -y
RUN apt-get install vim curl -y
RUN pip3 install --upgrade setuptools
RUN pip3 install xmltodict requests requests_oauthlib requests-oauth2
RUN mkdir -p /opt/bigid/discoverer
COPY discover_and_push.py /opt/bigid/discoverer/discover_and_push.py
COPY discover2file.py /opt/bigid/discoverer/discover2file.py
COPY import_ds_from_file.py /opt/bigid/discoverer/import_ds_from_file.py
COPY discover_sn.py /opt/bigid/discoverer/discover_sn.py
RUN curl -O https://nmap.org/dist/nmap-7.60.tar.bz2
RUN bzip2 -cd nmap-7.60.tar.bz2 | tar xvf -
RUN cd nmap-7.60 && ./configure && make && make install
WORKDIR /opt/bigid/discoverer
