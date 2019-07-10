"""Imports Data Sources from Service Now."""
import requests
import json
import os
import sys
import subprocess
from requests_oauth2 import OAuth2BearerToken


SN_USER = os.environ['DISCOVERER_SN_USER']  # 'admin'
SN_PWD = os.environ['DISCOVERER_SN_PWD']  # 'Ts@...'
SN_CLIENT_ID = os.environ['DISCOVERER_SN_CLIENT_ID']
SN_CLIENT_SECRET = os.environ['DISCOVERER_SN_CLIENT_SECRET']  # 'Ts@...'
SN_INSTANCE = os.environ['DISCOVERER_SN_INSTANCE']
SN_AUTH_TYPE = os.environ['DISCOVERER_SN_AUTH_TYPE']

BIGID_PWD = os.environ['DISCOVERER_BIGID_PWD']
BIGID_API_URL = os.environ['DISCOVERER_BIGID_API_URL']
DS_URL = BIGID_API_URL+'/ds_connections'
CREDS_URL = BIGID_API_URL+'/credentials'
SN_API_URL = 'https://' + SN_INSTANCE + '.service-now.com/api'


def get_sn_bToken():
    """Get an oAuth2 access_token from Service Now."""
    url = 'https://' + SN_INSTANCE + '.service-now.com/oauth_token.do'
    post_data = {
           'grant_type': 'password',
           'username': SN_USER,
           'password': SN_PWD,
           'client_id': SN_CLIENT_ID,
           'client_secret': SN_CLIENT_SECRET
    }

    response = requests.post(
           url,
           data=post_data
    )
    # Check for HTTP codes other than 200
    try:
        if response.status_code != 200:
                print('Status:', response.status_code, 'Headers:',
                      response.headers, 'Response:', response.json())
                print('Cookies', response.cookies)
        else:
            bToken = (response.json()["access_token"])
            return bToken
    except Exception:
        print("Something went wrong. Are youy connected to the internet?",
              sys.exc_info())


def create_obj(data, token, url):
    """Create entry in BigID."""
    print("Creating Entry...")
    print(data)
    subprocess.run(["curl", "-k", "-d", data, "-H",
                    "Content-Type: application/json", "-H", "x-access-token: "
                    + token, "-X", "POST", url])


def get_sn_config_items(url, token):
    """Get ci's from ServiceNow."""
    if SN_AUTH_TYPE == 'oAuth2':
        with requests.Session() as s:
            s.auth = OAuth2BearerToken(token)
            response = s.get(url)
            response.raise_for_status()
            data = response.json()
    else:
        headers = {"Accept": "application/json"}

        # Do the HTTP request
        response = requests.get(url, auth=(SN_USER, SN_PWD),
                                headers=headers)

    # Check for HTTP codes other than 200
    try:
        if response.status_code != 200:
                print('Status:', response.status_code, 'Headers:',
                      response.headers, 'Response:', response.json())
                print('Cookies', response.cookies)
        else:
            data = json.loads(json.dumps(response.json()))
            return data
    except Exception:
        print("Something went wrong. Are youy connected to the internet?",
              sys.exc_info())


def get_bigid_token():
    """Get an access token from BigID."""
    url = BIGID_API_URL+'/sessions'
    headers = {"Accept": "application/json"}
    data = {"username": "bigid", "password": BIGID_PWD}

    try:
        response = requests.post(url, data=data, headers=headers, verify=False)
        if response.status_code != 200:
                print('Status:', response.status_code, 'Headers:',
                      response.headers, 'Response:', response.json())
                print('Cookies', response.cookies)
        else:
            data = json.loads(json.dumps(response.json()))
            return (data["auth_token"])
    except Exception:
        print("Something went wrong. is BigID up?", sys.exc_info())


def parse_share_data(data, token):
    """Get attriubtes data from the share's xml entry."""
    shareName = (data["name"])
    # computerName = (entry["computer"])
    print(shareName)
    # print(data)
    if data["computer"] != "":
        computerLink = (json.loads(json.dumps(data["computer"]))["link"])
        # computerName = computerName["link"]
        # print(computerLink)
        # computer = get_sn_config_items(computerLink)
        computer = (json.loads(json.dumps(
           get_sn_config_items(computerLink, token))))
        computerName = (computer["result"]["name"])
        computerName = "".join(computerName.split("*"))
        computerIp = (computer["result"]["ip_address"])
        if computerIp == "":
            computerIp = computerName
        print(computerName + "\\" + shareName)
    else:
            print("\nNo computer associated with share " +
                  shareName + ". skipping entry.....\n")
            computerName = 'None'
            computerIp = 'None'
    return computerName, computerIp, shareName


def get_json_data(service, address, port, name, operational_status):
    """Get data by CI Type.Currently has MySQL,Postgress,Oracle,DB2."""
    """I need an ms sql entry example in ServiceNow."""
    if port != "":
        address = address + ":" + port
    if operational_status == "1":
        operational_status = "yes"
    name = 'SN_' + name.replace(" ", "_").replace("-", "_")
    print("\n" + name)
    dsDict = {
           # MySQL DS request body
           "MySQL": '{"ds_connection":{"name":"' + name +
           '", "credential_id": "rdb", "security_tier": "1",' +
           ' "rdb_is_sample_data": true, "rdb_url": "' +
           address + '", "type": "rdb-mysql", "scanner_strategy": "SCAN_ALL"' +
           ', "enabled": "' + operational_status +
           '", "differential": false, ' + '"is_idsor_supported": true' +
           ', "is_credential":true}}',
           # DB2 DS request body
           "DB2 UDB": '{"ds_connection":{"name":"' + name +
           '", "credential_id": "rdb", "security_tier": "1",' +
           ' "rdb_is_sample_data": true, "rdb_url": "' +
           address + '", "type": "rdb-db2", "scanner_strategy": "SCAN_ALL"' +
           ', "enabled": "' + operational_status + '", ' +
           '"differential": false, "is_idsor_supported": true' +
           ', "is_credential":true}}',
           # PostGres DS request body
           "Postgres SQL": '{"ds_connection":{"name":"' + name +
           '", "credential_id": "rdb", "security_tier": "1", ' +
           '"rdb_is_sample_data": true, "rdb_url": "' +
           address + '", "type": "rdb-postgresql", ' +
           '"scanner_strategy": "SCAN_ALL", "enabled": "' +
           operational_status +
           '", "differential": false, "is_idsor_supported": true' +
           ', "is_credential":true}}',
           # Oracle DS request body
           "Oracle": '{"ds_connection":{"client_secret":"",' +
           '"name":"' + name +
           '","credential_id":"rdb","rdb_is_sample_data":true,"rdb_url":"' +
           address + '","type":"rdb-oracle","security_tier":"1"' +
           ',"scanner_strategy":"SCAN_ALL"' +
           ',"enabled":"' + operational_status +
           '","differential":false,"is_idsor_supported":true' +
           ', "is_credential":true}}',
           # SMB DS request body
           "microsoft-ds": '{"ds_connection":{"name":"' + name +
           '", "credential_id": "smb" ,"security_tier": "1", ' +
           '"rdb_is_sample_data": false, "numberOfParsingThreads": "2",' +
           '"smbServer": "'+address+'", "type": "smb", ' +
           '"scanner_strategy": "SCAN_ALL", ' +
           '"enabled": "yes", "differential": false, "is_credential":true}}',
           # NFS DS request body
           "nfs": '{"ds_connection":{"client_secret":"","name":"' + name +
           '","credential_id":"nfs","numberOfParsingThreads":"2",' +
           '"rdb_is_sample_data":false,"nfsServer":"' + address + '","type"' +
           ':"nfs","security_tier":"1","scanner_strategy":"SCAN_ALL",' +
           '"enabled":"yes","differential":false, "is_credential":true}}'
       }
    data = str(dsDict.get(service))
    return(data)


def get_shares_json_data(type, name, address, sharedResource):
    """Get data for SMB and NFS."""
    name = 'SN_' + name.replace(" ", "_").replace("-", "_")
    dsDict = {
           # SMB DS request body
           "smb": '{"ds_connection":{' + '"name": "' +
           name + '",' + '"credential_id":"smb",' +
           '"sharedResource": "' + sharedResource +
           '" ,"numberOfParsingThreads":"2"' +
           ', "security_tier":"4",' +
           '"rdb_is_sample_data": false,' +
           '"smbServer": "' + address + '", "type": "smb",' +
           '"scanner_strategy": "SCAN_ALL",' + '"enabled": "yes",' +
           '"differential": false,"is_credential":true}}',
           # NFS DS request body
           "nfs": '{"ds_connection":{"client_secret":"","name":"' + name +
           '","credential_id":"nfs","numberOfParsingThreads":"2",' +
           '"rdb_is_sample_data":false,"nfsServer":"' + address + '","type"' +
           ':"nfs","security_tier":"1","scanner_strategy":"SCAN_ALL",' +
           '"enabled":"yes","differential":false,' +
           ' "is_credential":true,"sharedFolder":"' + sharedResource + '"}}'
       }
    data = str(dsDict.get(type))
    print(data)
    return(data)


def main():
    """Doc."""
    sn_token = get_sn_bToken()
    bigid_token = get_bigid_token()
    data = get_sn_config_items(SN_API_URL + '/now/table/cmdb_ci_database',
                               sn_token)
    # print(data)
    # print(data["result"][0]["operational_status"])
    for entry in data["result"]:
            operational_status = (entry["operational_status"])
            type = (entry["type"])
            name = (entry["name"])
            address = (entry["ip_address"])
            if address == "":
                address = name
            port = (entry["po_number"])
            if type == "":
                if "MySQL" in name:
                    type = "MySQL"
                if "Oracle" in name:
                    type = "Oracle"
                if "Postgres" in name:
                    type == "Postgres SQL"
                if "DB2" in name:
                    type == "DB2 UDB"
            else:
                type == "Unknown"

            print(address)
            if type != "Unknown" and address != "":
                post_data = get_json_data(type, address, port, name,
                                          operational_status)
                # print(post_data)
                create_obj(post_data, bigid_token, DS_URL)
            else:
                print("DS: " + name + " will not be imported - " +
                      "Insufficient data in CI record")
    # get smb shares
    data = get_sn_config_items(SN_API_URL + '/now/table/cmdb_ci_file_system_smb',
                               sn_token)
    for entry in data["result"]:
        computerName, computerIp, shareName = parse_share_data(entry, sn_token)
        if computerName != "None":
            post_data = get_shares_json_data("smb", computerName + "_" +
                                             shareName, computerIp, shareName)
            create_obj(post_data, bigid_token, DS_URL)
    # print(computerName)

    # get nfs shares
    data = get_sn_config_items(SN_API_URL + '/now/table/cmdb_ci_file_system_nfs',
                               sn_token)
    for entry in data["result"]:
        computerName, computerIp, shareName = parse_share_data(entry, sn_token)
        if computerName != "None":
            post_data = get_shares_json_data(
                "nfs", computerName + "_" + shareName, computerIp, shareName)
            create_obj(post_data, bigid_token, DS_URL)
    # print(computerName)


if __name__ == '__main__':
    main()
