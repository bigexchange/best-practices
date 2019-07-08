FROM python:3.6.7
LABEL maintainer="tals@bigid.com"
RUN apt-get update -y \
    && apt-get install vim curl sudo -y
RUN pip3 install --upgrade pip setuptools xmltodict requests requests_oauthlib requests-oauth2 pytz python-dateutil \
    && mkdir -p /opt/bigid/tasks_to_jira
WORKDIR /opt/bigid/tasks_to_sn
COPY tasks_sn.py tasks_to_tickets.sh create_categories.py insert_categories.sh ./
RUN useradd -u 2006 bigid \
    && echo "bigid ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/bigid \
    && chmod 0440 /etc/sudoers.d/bigid \
    && chown -R bigid:bigid /opt/bigid
USER bigid
ENV PATH /opt/bigid/tasks_to_sn:$PATH
CMD ["tasks_to_tickets.sh"]
