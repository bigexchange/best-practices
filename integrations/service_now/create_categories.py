
import json
import os
import sys
import requests
import urllib3
from requests.auth import HTTPBasicAuth
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


SN_USER = os.environ['SN_USER']
SN_PWD = os.environ['SN_PWD']
SN_INSTANCE = os.environ['SN_INSTANCE']


def add_sub_category(subCatName):
    """Add sub category."""
    print("Creating SubCategory: " + subCatName)
    auth = HTTPBasicAuth(SN_USER, SN_PWD)
    sn_uri = ("https://" + SN_INSTANCE +
              ".service-now.com/api/now/table/sys_choice")

    # define http headers for request
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        'name': 'incident',
        'element': 'subcategory',
        'label': subCatName,
        'value': subCatName,
        'dependent_value': 'Privacy Management',
        'language': 'en'
    }
    try:
        response = requests.post(url=sn_uri, data=json.dumps(payload),
                                 auth=auth, verify=False, headers=headers)
        print('Status:', response.status_code)
        if response.status_code == 200:
                print("Sub-Category allready exist")
        elif response.status_code == 201:
                print("Created Sub-Category")
        else:
                print('Status:', response.status_code)
    except Exception:
        print("Something went wrong.", sys.exc_info())


def add_category():
    """Add category."""
    print("Creating Category ")
    auth = HTTPBasicAuth(SN_USER, SN_PWD)
    sn_uri = ("https://" + SN_INSTANCE +
              ".service-now.com/api/now/table/sys_choice")

    # define http headers for request
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        'name': 'incident',
        'element': 'category',
        'label': 'Privacy Management',
        'value': 'Privacy Management',
        'language': 'en'
    }

    # Do the HTTP request
    try:
        response = requests.post(url=sn_uri, data=json.dumps(payload),
                                 auth=auth, verify=False, headers=headers)
        if response.status_code == 200:
                print("Category allready exist")
        elif response.status_code == 201:
                print("Created Category")
        else:
                print('Status:', response.status_code)
    except Exception:
        print("Something went wrong.", sys.exc_info())


def main():
    """Main."""
    choices = ['Full Report of an Individual', 'Deletion of an Individual',
               'Business Flows - Collaboration Request', 'Failed Scan',
               'Failed Policy', 'New Attribute Found', 'Service Down']
    print("adding category...")
    add_category()
    for choice in choices:
        add_sub_category(choice)
    print("done!")


if __name__ == '__main__':
    main()
