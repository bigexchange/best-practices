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


last_run_time = os.environ['LAST_RUN_TIME']
bigid_api_user = os.environ['BIGID_API_USER']
bigid_api_pwd = os.environ['BIGID_API_PWD']
bigid_api_url = os.environ['BIGID_API_URL']
bigid_tasks_url = os.environ['BIGID_TASKS_URL']
jira_user = os.environ['JIRA_USER']
jira_api_token = os.environ['JIRA_API_TOKEN']
jira_project = os.environ['JIRA_PROJECT']
jira_instance = ('https://' + os.environ['JIRA_INSTANCE'] +
                 '.atlassian.net')
# snGroup = os.environ['SN_GROUP']


def get_sub_category(taskType):
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
    data = str(categoryDict.get(taskType))
    return data


def get_bigid_token():
    """Get an access token from BigID."""
    print("Getting access token from BigID")
    url = bigid_api_url+'/sessions'
    headers = {"Accept": "application/json"}
    data = {"username": bigid_api_user, "password": bigid_api_pwd}

    # Do the HTTP request
    response = requests.post(
                            url, data=data, headers=headers, verify=False)
    print('Status:', response.status_code)
    if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:',
                  response.headers, 'Response:', response.json())
            print('Cookies', response.cookies)
            sys.exit(1)
    data = response.json()
    return (data["auth_token"])


def close_bigid_task(bigid_token, task_id):
    """Resolve task."""
    url = bigid_api_url + '/tasks/' + task_id
    # print(url)
    headers = {
        "Accept": "application/json",
        "authorization": bigid_token,
        "Content-Type": "application/json"
        }
    payload = {"status": "resolved"}


    # Do the HTTP request
    response = requests.put(
        url, data=json.dumps(payload), headers=headers, verify=False)
    # Check for HTTP codes other than 200
    if response.status_code != 200:
            print('Status:', response.status_code, "Operation failed!")
            exit()
    else:
            print(response.status_code, "Task closed!")


def get_tickets(bigid_token):
    """Get closed tickets from Jira ."""
    print("Checking for tasks to close")
    auth = HTTPBasicAuth(jira_user, jira_api_token)
    url = (jira_instance + '/rest/api/3/search?jql=project = ' + jira_project +
           ' AND issuetype = "Service Request" ' +
           'AND summary ~ "%BigID_Task%" ')
    # print(url)
    auth = HTTPBasicAuth(jira_user, jira_api_token)
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, auth=auth, headers=headers)
    if response.status_code != 200:
        print('Status:', response.status_code,
              'Headers:', response.headers, 'Error Response:', response.json())
        exit()
    data = (response.json())
    lastRun = datetime.strptime(last_run_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    lastRunutc = lastRun.replace(tzinfo=timezone('UTC'))
    for x in data["issues"]:
        ticketId = x['key']
        resolutionDate = x['fields']['resolutiondate']
        if resolutionDate is not None:
            resolutionDate = dateutil.parser.parse(resolutionDate)
            seconds_elapsed = (resolutionDate-lastRunutc).total_seconds()
            if seconds_elapsed >= 0:
                task_id = x['fields']['summary'].split("|")[1][:-1]
                print(ticketId + ' ' + task_id + ' ' + str(seconds_elapsed))
                close_bigid_task(bigid_token, task_id)


def jira_healthcheck():
    """HealthCheck."""
    print("Checking connection to Jira")
    auth = HTTPBasicAuth(jira_user, jira_api_token)
    url = jira_instance + '/status'

    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, auth=auth, headers=headers)

    print('Status:', response.status_code)
    if response.status_code != 200:
        sys.exit(2)


def find_user_by_mail(assigned_to):
    """Find Jira user by email."""
    url = jira_instance + "/rest/api/3/user/search?username=" + assigned_to
    auth = HTTPBasicAuth(jira_user, jira_api_token)
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, auth=auth, headers=headers)
    print('Status:', response.status_code)

    if response.status_code != 200:
        print('Status:', response.status_code,
              'Headers:', response.headers, 'Error Response:', response.json())
        exit()

    data = (response.json())
    username = ""
    for val in data:
        username = val["name"]
    return username


def create_jira_ticket(subject, description, subCategory, task_id, assigned_to):
    """Create a JIRA ticket with task details."""
    print("Creating Ticket for task_id: " + task_id)
    note = ("\n" + 'View in ' + bigid_tasks_url + '/' + task_id +
            ' for more details')
    assignee = find_user_by_mail(assigned_to)
    print("assignee: " + assignee)
    # jac = JIRA(jira_instance)
    options = {'server': jira_instance}
    jira = JIRA(options, basic_auth=(jira_user, jira_api_token))

    description = ("Category: " + subCategory + "\n" +
                   "Description: " + description + "\n\n\n" + note)
    if assignee != "":
            assignee = find_user_by_mail(jira_user)
    issue_dict = {
       'project': jira_project,
       'summary': subject + "  (BigID_Task|" + task_id+")",
       'description': description,
       'issuetype': {'name': 'Service Request'},
       'assignee': {'name': assignee}
    }
    new_issue = jira.create_issue(fields=issue_dict)
    print("+ JIRA issue created: {}".format(new_issue))


def main():
    """Flow starts here."""
    print("Performing healthcheck")
    bigid_token = get_bigid_token()
    jira_healthcheck()

    print("Checking for tickets to open")
    url = bigid_api_url+'/tasks?status=open&role=admin'
    # print(url)
    headers = {
            "Accept": "application/json;charset=utf-8",
            "Content-Type": "application/json",
            "x-access-token": bigid_token
    }
    response = requests.get(
                            url, headers=headers, verify=False)
    # Check for HTTP codes other than 200
    if response.status_code != 200:
            print('Status:', response.status_code, 'Headers:',
                  response.headers, 'Response:', response.json())
            print('Cookies', response.cookies)
            exit()
    data = json.loads(json.dumps(response.json()))

    lastRun = dateutil.parser.parse(str(last_run_time))
    lastRun = lastRun.replace(tzinfo=None)
    # compensate for lost tasks\tickets, or make system scan history
    # lastRun = lastRun - timedelta(0, 10)

    description = ""
    for entry in data:
        creation_date = entry['created_at']
        if creation_date is not None:
            creation_date = datetime.strptime(creation_date,
                                              '%Y-%m-%dT%H:%M:%S.%fZ')
            if creation_date >= lastRun:
                task_id = entry['_id']
                subCategory = get_sub_category(entry['type'])
                assigned_to = entry['owner']
                subject = entry['subject']
                for key, val in entry.items():
                    if 'comments' in key:
                        for attr, value in val[0].items():
                            if 'text' in attr:
                                description = value

                create_jira_ticket(subject, description, subCategory,
                             task_id, assigned_to)

    get_tickets(bigid_token)


if __name__ == '__main__':
    main()
