#!/bin/bash
docker cp discovery.csv discoverer:/opt/bigid/discoverer/
docker exec -it discoverer sh -c "python3 import_ds_from_file.py"
