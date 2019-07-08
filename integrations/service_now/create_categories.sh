#!/bin/bash
docker stop tasks2sn
docker rm tasks2sn
docker run -itd --name tasks2sn \
    -e SN_USER=admin \
		-e SN_PWD=changeme \
		-e SN_INSTANCE=myInstance \
		tals/tasks2sn:1.0.0 insert_categories.sh
