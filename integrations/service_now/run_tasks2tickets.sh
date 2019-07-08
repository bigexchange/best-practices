#!/bin/bash
docker stop tasks2sn
docker rm tasks2sn
docker run -itd --name tasks2sn \
	        -e BIGID_API_URL=https://172.17.0.1/api/v1 \
		-e BIGID_TASKS_URL=https://172.17.0.1/#/task-list \
		-e BIGID_API_USER=bigid \
                -e BIGID_API_PWD=changeme \
                -e SN_USER=admin \
		-e SN_PWD=changeme \
		-e SN_INSTANCE=myInstance \
		-e SN_GROUP=Software \
		-e SLEEP_TIME=30 \
		tals/tasks2sn:1.0.0
