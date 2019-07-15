#set -x
#!/bin/bash

echo -e "\n\nWe are now setting up BigID MongoDB automatic backup script. \n\n1. The first part collects the necessary Credentials and sets up the backup environment variables. \n\n2. The second Part will ask if you want to execute the first backup now, or execute manually at a later time.\n"
sleep 2

BACKUP_ROOT=~/db_backups
DEST=$BACKUP_ROOT/$DIR
SCRIPT_PATH=$BACKUP_ROOT/bin
mkdir -p $SCRIPT_PATH
cp backup.sh $SCRIPT_PATH

echo -e "\n====Part-1===="
echo -e "Collecting MongoDB Username Credentials to store in backup environment file:\n"
read -p "Please enter mongodb username (example: bigid): " BIGID_MONGO_USER
sed -i -e "s/^BIGID_MONGO_USER=.*/BIGID_MONGO_USER=$BIGID_MONGO_USER/" $SCRIPT_PATH/backup.sh

echo -e "\nCollecting MongoDB Credentials to store in backup environment file:\n"
read -s -p "Please enter mongodb password : " BIGID_MONGO_PWD
sed -i -e "s/^BIGID_MONGO_PWD=.*/BIGID_MONGO_PWD=$BIGID_MONGO_PWD/" $SCRIPT_PATH/backup.sh

echo -e "\nCollecting SSL Status to store in backup environment file:\n"
read -p "Does your mongoDB use SSL, Enter y or n: " SSL_TRUE
sed -i -e "s/^SSL_TRUE=.*/SSL_TRUE=$SSL_TRUE/" $SCRIPT_PATH/backup.sh
echo ""

case "$SSL_TRUE" in

	[y])
		read -p "Please enter full path to SSL CA Cert name inside mongodb (example: ca.pem): " CA_PEM
		sed -i -e"s/^CA_PEM=.*/CA_PEM=$CA_PEM/" $SCRIPT_PATH/backup.sh
		read -p "Please enter full path to SSL Server Cert name inside mongodb (example: server.pem): " SERVER_PEM
		sed -i -e"s/^SERVER_PEM=.*/SERVER_PEM=$SERVER_PEM/" $SCRIPT_PATH/backup.sh
		echo "Storing Backup variables and Certificate information to backup.sh"
		;;

	[n])
		echo -e "\n\nStoring backup variables to ${SCRIPT_PATH}/backup.sh\n\n"
		;;

esac
sleep 2

echo -e "\n====Part-2===="
read -p "Do you wish to proceed with the backup now?:(y/n) " BACKUP_NOW

case "$BACKUP_NOW" in

	[y])
		echo -e "\n\nexecuting backup for the first time and a weekly cron job will be setup for you:\n"
		sleep 2
		$SCRIPT_PATH/backup.sh
		;;

	[n])
		echo -e "\n\nYou can choose to execute the MongoDB backup script manually at a later time by executing ${SCRIPT_PATH}/backup.sh\n\n"
		sleep 2
		echo -e "\n					=======Goodbye=======\n\n"
		;;
esac