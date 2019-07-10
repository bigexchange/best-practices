#  BigID Community Content
</br>Welcome to the community content repository!
Since we want you to feel at home, we have decided to avoid long procedures. However, in order to avoid a mess, some mininal guidelines are required...

***

## Best Practices
**Secrets** - Do not push secrets. Pay attention that secrets are still available in git log, no matter if you deleted them in a later commit.</br>
**Language** - Although we appreciate any contribution, we prefer Python 3.x</br>
**Notify content maintainers** - When issuing a pull request, please add an admin **and the original developer** of the tool you are changing  as reviewers.</br>
**Testing** - Test your stuff and provide a README.</br>
**Packaging** - Dockerize your code, else supply an installation script or installation instructions for all dependencies.</br>
</br></br>


## Naming and Coding Conventions
Use snake_case for functions and variable names:
```python
creation_date = entry['created_at']
```
Use SNAKE_CASE for global variables:
```python
BIGID_API_USER = os.environ['BIGID_API_USER']
```
Catch exceptions:
```python
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
```

</br>In general, try to follow the pep8 style guide (https://www.python.org/dev/peps/pep-0008/)

</br></br>
## Docker Best Practices
Add a build script with proper tagging:
```docker
docker build -t tals/tasks2jira:1.0.0 .
```
Add a maintainer lable to your Dockerfile:
```docker
LABEL maintainer="elvis@example.com"
```
Avoid running as root by adding a USER instruction:
```docker
USER bigid
```
</br>In general, try to follow Docker's best practices (https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

</br></br>
In case you would like to contribute, please [contact us](https://bigid.com/contact/)  and we will grant you with collaborator permissions.</br></br></br>


## Have fun!

![](https://media.licdn.com/dms/image/C4D0BAQG8O65N7UpNRw/company-logo_200_200/0?e=2159024400&v=beta&t=gKnWLC3hKdOhdruqxohiEPPyPc7ziDNcH_CiGOkH32c)
