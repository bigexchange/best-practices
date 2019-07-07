#!/bin/bash
docker stop tasks2jira
docker rm tasks2jira
docker run -itd --name tasks2jira \
	        -e BIGID_API_URL=https://172.17.0.1/api/v1 \
		-e BIGID_TASKS_URL=https://172.17.0.1/#/task-list \
		            -e BIGID_API_USER=bigid \
                -e BIGID_API_PWD=bigid111 \
                -e JIRA_USER=changeme@example.com \
		-e JIRA_API_TOKEN=myApiToken \
		-e JIRA_PROJECT=TT \
		-e JIRA_INSTANCE=myInstanceName \
		-e SLEEP_TIME=30 \
		tals/tasks2jira:1.0.0
