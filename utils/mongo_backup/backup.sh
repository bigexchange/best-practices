#set -x
#!/bin/bash

BIGID_MONGO_USER=someusername
BIGID_MONGO_PWD=somepassword
SSL=y
SSL_TRUE=y
CA_PEM=ca.pem
SERVER_PEM=server.pem

DIR=$(date +%m-%d-%Y_%H_%M_%S)
BACKUP_ROOT=~/db_backups
DEST=$BACKUP_ROOT/$DIR
SCRIPT_PATH=$BACKUP_ROOT/bin

if [ "$SSL_TRUE" = "SSL" ]
then

docker exec bigid-mongo /bin/bash -c 'mongodump -h bigid-mongo:27017 -u '$BIGID_MONGO_USER' -p '$BIGID_MONGO_PWD' --ssl --sslCAFile=$CA_PEM --sslPEMKeyFile=$SERVER_PEM --authenticationDatabase=admin --gzip > backup_local.sh'

else

docker exec bigid-mongo /bin/bash -c 'mongodump -h localhost -u '$BIGID_MONGO_USER' -p '$BIGID_MONGO_PWD' --authenticationDatabase=admin --gzip > backup_local.sh'

fi

docker cp bigid-mongo:/dump $DEST
cd $BACKUP_ROOT && tar -zcvf $DIR.tar.gz $DIR
docker exec bigid-mongo /bin/bash -c `cd /dump && rm -r *`
rm -r $DIR

#delete all backup files except the newest 3
ls *.tar.gz -t | tail -n +4 | xargs rm --

crontab -l > mycron

#backup every weekend at 6 AM
# m h dom mon dow command
grep -qxF "0 06 * * 7 $SCRIPT_PATH/backup.sh" mycron || echo  "0 06 * * 7 $SCRIPT_PATH/backup.sh $BIGID_MONGO_USER $BIGID_MONGO_PWD" >> mycron
crontab mycron

echo -e "\n\nbackup is finished and scheduled with the following crontab:\n"
echo -e "mintue|hour|day-of-month|month|day-of-week|command"
crontab -l

echo -e '\nif you see more then 1 line running the backup, update crontab manually using "crontab -e"'