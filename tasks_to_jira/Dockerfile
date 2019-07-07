FROM python:3.6.7
RUN apt-get update -y
RUN apt-get install vim curl -y
RUN pip3 install --upgrade setuptools
RUN pip3 install xmltodict requests requests_oauthlib requests-oauth2 pytz python-dateutil jira
RUN mkdir -p /opt/bigid/tasks_to_jira
WORKDIR /opt/bigid/tasks_to_jira
COPY tasks_jira.py /opt/bigid/tasks_to_jira/tasks_jira.py
COPY tasks_to_tickets_p3.sh /opt/bigid/tasks_to_jira/tasks_to_tickets_p3.sh
CMD ["/opt/bigid/tasks_to_jira/tasks_to_tickets_p3.sh"]
