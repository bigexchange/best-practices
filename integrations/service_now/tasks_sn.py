
import json
import os
import sys
import requests
import urllib3
import dateutil.parser
from datetime import datetime
# from datetime import timedelta
from pytz import timezone
from requests.auth import HTTPBasicAuth
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LAST_RUN_TIME = os.environ['LAST_RUN_TIME']
BIGID_API_USER = os.environ['BIGID_API_USER']
BIGID_API_PWD = os.environ['BIGID_API_PWD']
BIGID_API_URL = os.environ['BIGID_API_URL']
BIGID_TASKS_URL = os.environ['BIGID_TASKS_URL']
SN_USER = os.environ['SN_USER']
SN_PWD = os.environ['SN_PWD']
SN_INSTANCE = os.environ['SN_INSTANCE']
SN_GROUP = os.environ['SN_GROUP']


def get_sub_category(task_type):
    """Translate Task type to Service Now category."""
    categoryDict = {
      "delete-user-task": "Deletion of an Individual",
      "collaboration": "Business Flows - Collaboration Request",
      "failedScan": "Failed Scan",
      "complianceRule": "Failed Policy",
      "jit-scan-task": "Full Report of an Individual",
      "attributeWithoutPurpose": "New Attribute Found",
      "serviceDown": "Service Down"
    }
    data = str(categoryDict.get(task_type))
    return data


def get_sn_user(user):
    """Check if task owner exists in Service Now."""
    print("Checking if Task Owner is an Active Service Now User")
    auth = HTTPBasicAuth(SN_USER, SN_PWD)
    url = ("https://" + SN_INSTANCE +
           ".service-now.com/api/now/table/sys_user" +
           "?sysparm_query=email=" + user + "&active=true")

    headers = {"Accept": "application/json"}
    try:
        response = requests.get(url, auth=auth, headers=headers, verify=False)

        if response.status_code != 200:
            print('Status:', response.status_code,
                  'Headers:', response.headers, 'Error Response:',
                  response.json())
        else:
            data = (response.json())
            sn_user_id = ""
            for val in data["result"]:
                sn_user_id = (val["email"])

            return (sn_user_id)
    except Exception:
        print("Something went wrong.", sys.exc_info())


def get_bigid_token():
    """Get an access token from BigID."""
    print("Getting access token from BigID")
    url = BIGID_API_URL+'/sessions'
    headers = {"Accept": "application/json"}
    data = {"username": BIGID_API_USER, "password": BIGID_API_PWD}

    # Do the HTTP request
    try:
        response = requests.post(
                                url, data=data, headers=headers, verify=False)
        print(response.status_code)
        if response.status_code != 200:
                print('Status:', response.status_code, 'Headers:',
                      response.headers, 'Response:', response.json())
                print('Cookies', response.cookies)
        else:
            data = response.json()
            return (data["auth_token"])
    except Exception:
        print("Something went wrong.", sys.exc_info())


def close_bigid_task(bigid_token, task_id):
    """Resolve task."""
    url = BIGID_API_URL + '/tasks/' + task_id
    # print(url)
    headers = {
        "Accept": "application/json",
        "authorization": bigid_token,
        "Content-Type": "application/json"
        }
    payload = {"status": "resolved"}

    # Do the HTTP request
    try:
        response = requests.put(
            url, data=json.dumps(payload), headers=headers, verify=False)
        # Check for HTTP codes other than 200
        if response.status_code != 200:
                print('Status:', response.status_code, "Operation failed!")
        else:
                print(response.status_code, "Task closed!")
    except Exception:
        print("Something went wrong.", sys.exc_info())


def get_sn_tickets(bigid_token):
    """Get resolved tickets from ServiceNow."""
    print("Checking for tasks to close")
    auth = HTTPBasicAuth(SN_USER, SN_PWD)
    url = ("https://" + SN_INSTANCE +
           ".service-now.com/api/now/table/incident" +
           "?sysparm_query=short_descriptionLIKEBigID_Task|&state=Resolved")

    headers = {"Accept": "application/json"}
    try:
        response = requests.get(url, auth=auth, headers=headers, verify=False)

        if response.status_code != 200:
            print('Status:', response.status_code,
                  'Headers:', response.headers, 'Error Response:',
                  response.json())
        else:
            data = (response.json())
            for val in data["result"]:
                short_desc = val["short_description"]
                task_id = short_desc.split("|")[1][:-1]
                resolve_date = val["resolved_at"]
                last_run = datetime.strptime(LAST_RUN_TIME,
                                             '%Y-%m-%dT%H:%M:%S.%fZ')
                resolve_dt = datetime.strptime(resolve_date,
                                               '%Y-%m-%d %H:%M:%S')
                last_run_utc = last_run.replace(tzinfo=timezone('UTC'))
                resolve_dtutc = resolve_dt.replace(tzinfo=timezone('UTC'))

                seconds_elapsed = (resolve_dtutc-last_run_utc).total_seconds()
                if seconds_elapsed >= 0:
                    print("Closing BigID task " + task_id)
                    close_bigid_task(bigid_token, task_id)
    except Exception:
        print("Something went wrong.", sys.exc_info())


def create_sn_ticket(sn_user_id, subject, description, task_id, sub_category):
    """Create an SN ticket with task details."""
    print("Creating Ticket for task_id: " + task_id)
    auth = HTTPBasicAuth(SN_USER, SN_PWD)
    sn_uri = "https://" + SN_INSTANCE + ".service-now.com/incident.do?JSONv2"

    # define http headers for request
    headers = {
        "Accept": "application/json;charset=utf-8",
        "Content-Type": "application/json"
    }

    if sn_user_id != "":
            payload = {
                'sysparm_action': 'insert',
                'category': 'Privacy Management',
                'subcategory': sub_category,
                'impact': '1',
                'urgency': '1',
                'short_description': subject + "  (BigID_Task|" + task_id+")",
                'description': description,
                'caller_id': 'BigID_API',
                'assigned_to': sn_user_id,
                'work_notes': '[code]<p>View in <a href=' + BIGID_TASKS_URL +
                '/' + task_id +
                ' target="_blank">BigID</a> for more details</p>[/code]'
            }
    else:
            print("The assigned user does not exist or inactive in " +
                  " Service Now\n\nAssigning to default group: " + SN_GROUP)
            payload = {
                'sysparm_action': 'insert',
                'category': 'Privacy Management',
                'subcategory': sub_category,
                'impact': '1',
                'urgency': '1',
                'short_description': subject + "  (BigID_Task|" + task_id+")",
                'description': description,
                'caller_id': 'BigID_API',
                'assignment_group': SN_GROUP,
                'work_notes': '[code]<p>View in <a href=' +
                BIGID_TASKS_URL + '/' + task_id +
                ' target="_blank">BigID</a> for more details</p>[/code]'
            }

    # Do the HTTP request
    try:
        response = requests.post(url=sn_uri, data=json.dumps(payload),
                                 auth=auth, verify=False, headers=headers)

        if response.status_code != 200:
                print('Status:', response.status_code)
        else:
                print("Created a Ticket for task_id:" + task_id)
    except Exception:
        print("Something went wrong.", sys.exc_info())


def main():
    """Flow starts here."""
    bigid_token = get_bigid_token()
    print("Checking for tickets to open")
    url = BIGID_API_URL+'/tasks?status=open&role=admin'
    # print(url)
    headers = {
            "Accept": "application/json;charset=utf-8",
            "Content-Type": "application/json",
            "x-access-token": bigid_token
    }
    try:
        response = requests.get(
                                url, headers=headers, verify=False)
        # Check for HTTP codes other than 200
        if response.status_code != 200:
                print('Status:', response.status_code, 'Headers:',
                      response.headers, 'Response:', response.json())
                print('Cookies', response.cookies)
        data = json.loads(json.dumps(response.json()))

        last_run = dateutil.parser.parse(str(LAST_RUN_TIME))
        last_run = last_run.replace(tzinfo=None)
        description = ""
        for entry in data:
            creation_date = entry['created_at']
            if creation_date is not None:
                creation_date = datetime.strptime(creation_date,
                                                  '%Y-%m-%dT%H:%M:%S.%fZ')
                if creation_date >= last_run:
                    task_id = entry['_id']
                    sub_category = get_sub_category(entry['type'])
                    assigned_to = entry['owner']
                    subject = entry['subject']
                    for key, val in entry.items():
                        if 'comments' in key:
                            for attr, value in val[0].items():
                                if 'text' in attr:
                                    description = value
                    sn_user_id = get_sn_user(assigned_to)
                    print("sn user id: " + sn_user_id)
                    create_sn_ticket(sn_user_id, subject, description,
                                     task_id, sub_category)

        get_sn_tickets(bigid_token)
    except Exception:
        print("Something went wrong.", sys.exc_info())


if __name__ == '__main__':
    main()
