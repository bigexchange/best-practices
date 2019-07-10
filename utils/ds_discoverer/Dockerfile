FROM python:3.6.7
RUN apt-get update -y && apt-get install vim curl -y
# RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade setuptools xmltodict requests requests_oauthlib requests-oauth2
RUN mkdir -p /opt/bigid/discoverer
WORKDIR /opt/bigid/discoverer
COPY discover2file.py import_ds_from_file.py discover_sn.py ./
RUN curl -O https://nmap.org/dist/nmap-7.60.tar.bz2
RUN bzip2 -cd nmap-7.60.tar.bz2 | tar xvf -
RUN cd nmap-7.60 && ./configure && make && make install
