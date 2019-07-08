#!/bin/bash

if [ -z ${LAST_RUN_TIME+x} ];
   then export LAST_RUN_TIME=$( date --utc '+%FT%T.%3NZ' )
fi
while true
do
   python3 tasks_jira.py
   if [ $? -eq 0 ]
     then export LAST_RUN_TIME=$( date --utc '+%FT%T.%3NZ' )
   else
     echo "failed."
   fi
   echo "going back to sleep for $SLEEP_TIME seconds...."
   sleep $SLEEP_TIME
done
