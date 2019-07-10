"""Scan network and create data sources."""

import json
import os
import requests
import subprocess
import csv

BIGID_API_URL = os.environ['DISCOVERER_BIGID_API_URL']
BIGID_API_PASSWORD = os.environ['DISCOVERER_BIGID_PWD']
DS_URL = BIGID_API_URL+'/ds_connections'
CREDS_URL = BIGID_API_URL+'/credentials'
# CREATE_CREDS = 1
DS_FILE = 'discovery.csv'
# e.g. https://localhost/api/v1


def get_bigid_token():
    """Get an access token from BigID."""
    url = BIGID_API_URL+'/sessions'
    headers = {"Accept": "application/json"}
    data = {"username": "bigid", "password": BIGID_API_PASSWORD}

    # Do the HTTP request
    response = requests.post(
                            url, data=data, headers=headers, verify=False)
    # Check for HTTP codes other than 200
    if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:',
                  response.headers, 'Response:', response.json())
            print('Cookies', response.cookies)

    data = json.loads(json.dumps(response.json()))
    return (data["auth_token"])


'''
def get_credentials_data(credsType):
    """Prepare Credentials http body by scan type."""
    credsDict = {
        "rdb": """{"credential_id":"rdb","username": "rdbadmin",
        "password":"123456"}""",
        "smb": """{"credential_id":"smb","username": "smbadmin",
        "password":"123456"}""",
        "nfs": """{"credential_id":"nfs","username": "nfsadmin",
        "password":"123456"}"""
    }
    data = str(credsDict.get(credsType))
    return data
'''


def get_json_data(service, row, sharedResource):
    """Prepare DS http body by Service Name."""
    if len(sharedResource) > 0:
                sharedResource = (',"sharedResource":"' +
                                  row["sharedResource"] + '"')
    dsDict = {
        # MySQL DS request body
        "rdb-mysql": '{"ds_connection":{"name":"' + row["name"] +
        '", "credential_id": "' + row["credential_id"] +
        '", "security_tier": "' + row["security_tier"] +
        '","rdb_is_sample_data": ' + row["rdb_is_sample_data"] +
        ', "rdb_url": "' + row["rdb_url"] + '", "type": "' +
        row["type"] + '", "scanner_strategy": "' + row["scanner_strategy"] +
        '","enabled": "' + row["enabled"] + '", "differential": ' +
        row["differential"] + ' ,"is_credential":true}}',
        # MS-SQL DS request body
        "rdb-mssql": '{"ds_connection":{"name":"' + row["name"] +
        '", "credential_id": "' + row["credential_id"] +
        '", "security_tier": "' + row["security_tier"] +
        '","rdb_is_sample_data": ' + row["rdb_is_sample_data"] +
        ', "rdb_url": "' + row["rdb_url"] + '", "type": "' +
        row["type"] + '", "scanner_strategy": "' + row["scanner_strategy"] +
        '","enabled": "' + row["enabled"] + '", "differential": ' +
        row["differential"] + ', "is_credential":true}}',
        # PostGres DS request body
        "rdb-postgresql": '{"ds_connection":{"name":"' + row["name"] +
        '", "credential_id": "' + row["credential_id"] +
        '", "security_tier": "' + row["security_tier"] +
        '","rdb_is_sample_data": ' + row["rdb_is_sample_data"] +
        ', "rdb_url": "' + row["rdb_url"] + '", "type": "' +
        row["type"] + '", "scanner_strategy": "' + row["scanner_strategy"] +
        '","enabled": "' + row["enabled"] + '", "differential": ' +
        row["differential"] + ', "is_credential":true}}',
        # Oracle DS request body
        "rdb-oracle": '{"ds_connection":{"name":"' + row["name"] +
        '", "credential_id": "' + row["credential_id"] +
        '", "security_tier": "' + row["security_tier"] +
        '","rdb_is_sample_data": ' + row["rdb_is_sample_data"] +
        ', "rdb_url": "' + row["rdb_url"] + '", "type": "' +
        row["type"] + '", "scanner_strategy": "' + row["scanner_strategy"] +
        '","enabled": "' + row["enabled"] + '", "differential": ' +
        row["differential"] + ', "is_credential":true}}',
        # SMB DS request body
        "smb": '{"ds_connection":{"name":"' + row["name"] +
        '", "credential_id": "' + row["credential_id"] +
        '" ,"security_tier": "' + row["security_tier"] +
        '", "rdb_is_sample_data": ' + row["rdb_is_sample_data"] +
        ', "numberOfParsingThreads": "2","smbServer": "' + row["rdb_url"] +
        '", "type": "smb", "scanner_strategy": "' + row["scanner_strategy"] +
        '", "enabled": "' + row["enabled"] + '", "differential": ' +
        row["differential"] + sharedResource + ',"is_credential":true}}',
        # NFS DS request body
        "nfs": '{"ds_connection":{"client_secret":"","name":"' + row["name"] +
        '","credential_id":"' + row["credential_id"] +
        '","numberOfParsingThreads":"2",' +
        '"rdb_is_sample_data":' + row["rdb_is_sample_data"] +
        ',"nfsServer":"' + row["rdb_url"] + '","type":"' + row["type"] +
        '","security_tier":"' + row["security_tier"] +
        '","scanner_strategy":"' + row["scanner_strategy"] + '","enabled":"' +
        row["enabled"] + '","differential":' + row["differential"] +
        ', "is_credential":true}}',
        # MongoDB DS request body
        "mongodb": '{"ds_connection":{"client_secret":"","name":"' +
        row["name"] + '","credential_id":"' + row["credential_id"] +
        '","rdb_is_sample_data":true,"mongo_url":"' +
        row["rdb_url"] + '","mongo_db_name":"","is_credential":true,"type":"' +
        row["type"] + '","security_tier":"' + row["security_tier"] +
        '","scanner_strategy":"' + row["scanner_strategy"] + '","enabled":"' +
        row["enabled"] + '", "differential":' + row["differential"] +
        '}}',
       }

    data = str(dsDict.get(service))
    return(data)


def csv_processor(token):
    """Process scan results and perform imports."""
    print("preparing scan results for import...")
    with open(DS_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            # data = '({row["name"]}'
            type = row["type"]
            sharedResource = row["sharedResource"]
            data = get_json_data(type, row, sharedResource)
            if str(data) != "None":
                print('\n' + data)
                create_obj(data, token, DS_URL)
            line_count += 1


def create_obj(data, token, url):
    """Create entries in BigID."""
    print("data:" + data)
    if data != "":
        print("\nCreating Entry...")
        subprocess.run(
            ["curl", "-k", "-d", data, "-H", "Content-Type: application/json",
             "-H", "x-access-token:" + token, "-X", "POST", url])
    else:
        print ("data is None")


'''
def get_bigid_data(url, bigid_token):
    """Get data from BigID."""
    headers = {"Accept": "application/json", "x-access-token": bigid_token}
    response = requests.get(url, auth=('admin', BIGID_API_PASSWORD),
                            headers=headers, verify=False)

    # Check for HTTP codes other than 200
    if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:',
                  response.headers, 'Response:', response.json())
            print('Cookies', response.cookies)

    data = json.loads(json.dumps(response.json()))
    return data
'''


def main():
    """Flow starts here."""
    bigid_token = get_bigid_token()
    print(bigid_token)
    for type in ("rdb-oracle", "rdb-mssql", "rdb-postgresql", "rdb-mysql",
                 "smb", "nfs", "mongodb"):
        credsData = ('{"credential_id":"' + type + '","username": "' +
                     type + '-admin","password":"123456"}')
        create_obj(credsData, bigid_token, CREDS_URL)
    csv_processor(bigid_token)
    print('\nDone. please check BigID for data source names ' +
          'which start with "auto-discovered"')


if __name__ == '__main__':
    main()
