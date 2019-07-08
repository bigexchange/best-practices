## Create Service incidents for BigID tasks



## Setup Instructions:

1. Run build_image.sh
2. Update create_categories.sh with your credentials and run it.

Option A: Run in a seperate container
1. Update run_tasks2tickets.sh with your credentials
2. Run run_tasks2tickets.sh

Option B (recommended): Run as part of the BigID services:
1. Add the content of setenv.txt to your setenv.sh and update it with your environment variables values.
2. Add the the content of compose.txt to your docker-compose file (bigid-all-compose.yml or bigid-ext-mongo-compose.yml).
3. start bigid as usual with the script which usesd your compose file (run-bigid-all.sh or run-bigid-ext-mongo.sh).
   A container named bigid-tasks2sn will be created.


Test your setup:
1. Create a task. After 60 seconds a ticket will be created at https://your_instance.service-now.com/nav_to.do?uri=%2Fincident_list.do
2. If you resolve the ticket, after 60 seconds the task will be resolved.


In case you have any questios, or you want to contribute to this one, please contact tals@bigid.com

