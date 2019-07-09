#!/bin/bash
docker stop discoverer
docker rm discoverer
docker run -itd --name discoverer \
       	-e DISCOVERER_IP_RANGE=10.2.0.1-254 \
       	-e DISCOVERER_SCAN_TYPE=smb \
	-e DISCOVERER_BIGID_API_URL=https://172.21.0.1/api/v1 \
        -e DISCOVERER_BIGID_PWD=changeme \
	tals/discoverer:1.0.2 bash
docker exec -it discoverer sh -c "python3 discover2file.py"
docker cp discoverer:/opt/bigid/discoverer/discovery.csv .
