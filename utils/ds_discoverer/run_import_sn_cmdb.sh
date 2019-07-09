#!/bin/bash
docker stop discoverer
docker rm discoverer
docker run -itd --name discoverer \
	-e DISCOVERER_SN_CLIENT_ID=ServiceNow_client_ID \
	-e DISCOVERER_SN_CLIENT_SECRET=changeme \
	-e DISCOVERER_SN_INSTANCE=ServiceNow_instance._e.g.:dev57440 \
	-e DISCOVERER_SN_AUTH_TYPE=oAuth2 \
	-e DISCOVERER_SN_USER=admin \
	-e DISCOVERER_SN_PWD=changeme \
	-e DISCOVERER_BIGID_API_URL=https://172.17.0.1/api/v1 \
	-e DISCOVERER_BIGID_PWD=changeme \
	tals/discoverer:1.0.2 bash
docker exec -it discoverer sh -c "python3 discover_sn.py"
