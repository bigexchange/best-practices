"""Create Jira incidents for BigID tasks."""
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
from jira import JIRA
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LAST_RUN_TIME = os.environ['LAST_RUN_TIME']
BIGID_API_USER = os.environ['BIGID_API_USER']
BIGID_API_PWD = os.environ['BIGID_API_PWD']
BIGID_API_URL = os.environ['BIGID_API_URL']
BIGID_TASKS_URL = os.environ['BIGID_TASKS_URL']
JIRA_USER = os.environ['JIRA_USER']
JIRA_API_TOKEN = os.environ['JIRA_API_TOKEN']
JIRA_PROJECT = os.environ['JIRA_PROJECT']
JIRA_INSTANCE = ('https://' + os.environ['JIRA_INSTANCE'] +
                 '.atlassian.net')


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
        print('Status:', response.status_code)
        if response.status_code != 200:
                print('Status:', response.status_code, 'Headers:',
                      response.headers, 'Response:', response.json())
                print('Cookies', response.cookies)
        else:
            data = response.json()
            return (data["auth_token"])
    except Exception:
        print("Something went wrong. Is BigID up?", sys.exc_info())


def close_bigid_task(bigid_token, task_id):
    """Resolve task."""
    url = BIGID_API_URL + '/tasks/' + task_id
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
        print("Something went wrong. Is BigID up?", sys.exc_info())


def get_tickets(bigid_token):
    """Get closed tickets from Jira ."""
    print("Checking for tasks to close")
    auth = HTTPBasicAuth(JIRA_USER, JIRA_API_TOKEN)
    url = (JIRA_INSTANCE + '/rest/api/3/search?jql=project = ' + JIRA_PROJECT +
           ' AND issuetype = "Service Request" ' +
           'AND summary ~ "%BigID_Task%" ')
    headers = {"Accept": "application/json"}

    try:
        response = requests.request("GET", url, auth=auth, headers=headers)
        if response.status_code != 200:
            print('Status:', response.status_code,
                  'Headers:', response.headers, 'Error Response:',
                  response.json())
        else:
            data = (response.json())
            last_run = datetime.strptime(LAST_RUN_TIME,
                                         '%Y-%m-%dT%H:%M:%S.%fZ')
            last_run_utc = last_run.replace(tzinfo=timezone('UTC'))
            for x in data["issues"]:
                ticketId = x['key']
                resolutionDate = x['fields']['resolutiondate']
                if resolutionDate is not None:
                    resolutionDate = dateutil.parser.parse(resolutionDate)
                    seconds_elapsed = (resolutionDate-last_run_utc).total_seconds()
                    if seconds_elapsed >= 0:
                        task_id = x['fields']['summary'].split("|")[1][:-1]
                        print(ticketId + ' ' + task_id + ' ' +
                              str(seconds_elapsed))
                        close_bigid_task(bigid_token, task_id)
    except Exception:
        print("Something went wrong.", sys.exc_info())


def find_user_by_mail(assigned_to):
    """Find Jira user by email."""
    url = JIRA_INSTANCE + "/rest/api/3/user/search?username=" + assigned_to
    auth = HTTPBasicAuth(JIRA_USER, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    try:
        response = requests.request("GET", url, auth=auth, headers=headers)
        print('Status:', response.status_code)

        if response.status_code != 200:
            print('Status:', response.status_code,
                  'Headers:', response.headers, 'Error Response:',
                  response.json())
        else:
            data = (response.json())
            username = ""
            for val in data:
                username = val["name"]
            return username

    except Exception:
        print("Cannot reach Jira", sys.exc_info())


def create_jira_ticket(subject, description, sub_category,
                       task_id, assigned_to):
    """Create a JIRA ticket with task details."""
    print("Creating Ticket for task_id: " + task_id)
    note = ("\n" + 'View in ' + BIGID_TASKS_URL + '/' + task_id +
            ' for more details')
    assignee = find_user_by_mail(assigned_to)
    print("assignee: " + assignee)
    # jac = JIRA(JIRA_INSTANCE)
    options = {'server': JIRA_INSTANCE}
    jira = JIRA(options, basic_auth=(JIRA_USER, JIRA_API_TOKEN))

    description = ("Category: " + sub_category + "\n" +
                   "Description: " + description + "\n\n\n" + note)
    if assignee != "":
            assignee = find_user_by_mail(JIRA_USER)
    issue_dict = {
       'project': JIRA_PROJECT,
       'summary': subject + "  (BigID_Task|" + task_id+")",
       'description': description,
       'issuetype': {'name': 'Service Request'},
       'assignee': {'name': assignee}
    }
    new_issue = jira.create_issue(fields=issue_dict)
    print("+ JIRA issue created: {}".format(new_issue))


def main():
    """Flow starts here."""
    bigid_token = get_bigid_token()

    print("Checking for tickets to open")
    url = BIGID_API_URL+'/tasks?status=open&role=admin'
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
        else:
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

                        create_jira_ticket(subject, description, sub_category,
                                           task_id, assigned_to)

        get_tickets(bigid_token)

    except Exception:
        print("Cannot reach BigID", sys.exc_info())


if __name__ == '__main__':
    main()
