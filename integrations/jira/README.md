
## Create Service incidents for BigID tasks



## Setup Instructions:

1. Add the content of setenv.txt to your setenv.sh and update it with your environment variables values.
2. Add the the content of compose.txt to your docker-compose file (bigid-all-compose.yml or bigid-ext-mongo-compose.yml).
3. Start bigid as usual with the script which usesd your compose file (run-bigid-all.sh or run-bigid-ext-mongo.sh).
   The image will be pulled and a container named bigexchange-tasks2jira will be created.


Test your setup:
1. Create a task. After 60 seconds a ticket will be created in Jira ServiceDesk
2. If you resolve the ticket, once the no seconds which was defined in the SLEEP_TIME environment variable is exceeded, the task will be resolved.


In case you have any questios, or you want to contribute to this one, please contact tals@bigid.com
