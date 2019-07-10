#!/bin/bash
#edited by morgan 
#removed hardcoded passwords as a first requirement
if [ $# != 2 ]; then
     echo "Your command should contain 2 arguments."
     echo "Use the following syntax: backup.sh <mongo user> <mongo password>"
     exit
fi

BIGID_MONGO_USER=$1
BIGID_MONGO_PWD=$2
echo 'for better security it is recommended to chmod 600 the file, and rename it to start with a "."'
sleep 5

DIR=$(date +%m-%d-%Y_%H_%M_%S)
BACKUP_ROOT=~/db_backups
DEST=$BACKUP_ROOT/$DIR
SCRIPT_PATH=$BACKUP_ROOT/bin
mkdir -p $DEST
mkdir -p $SCRIPT_PATH
cp backup.sh $SCRIPT_PATH
docker exec bigid-mongo /bin/bash -c 'mongodump -h localhost -u '$BIGID_MONGO_USER' -p '$BIGID_MONGO_PWD' --authenticationDatabase=admin --gzip > backup_local.sh'
docker cp bigid-mongo:/dump $DEST
cd $BACKUP_ROOT && tar -zcvf $DIR.tar.gz $DIR
docker exec bigid-mongo /bin/bash -c 'cd /dump && rm -r *'
rm -r $DIR

#delete all backup files except the newest 3.
ls *.tar.gz -t | tail -n +4 | xargs rm --

crontab -l > mycron

#backup every weekend at 6 AM
 # m h dom mon dow command
grep -qxF "0 06 * * 7 $SCRIPT_PATH/db_backup.sh" mycron || echo  "0 06 * * 7 $SCRIPT_PATH/db_backup.sh $BIGID_MONGO_USER $BIGID_MONGO_PWD" >> mycron
crontab mycron

echo -e "\n\nbackup is finished and scheduled with the following crontab:\n"
echo -e "mintue|hour|day-of-month|month|day-of-week|command"
crontab -l

echo -e '\nif you see more then 1 line running the backup, update crontab manually using "crontab -e"'
