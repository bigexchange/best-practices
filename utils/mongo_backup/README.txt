Mongodb Backup

1. There are two scripts provided to perform the BigID-mongodb backup
2. First Scipt 'init-backup.sh' is to be executed ONCE
	- sets up the directory/files to store backup.sh
	- collects variables for:

	a. mongodb 'username' and stores variable to ==> BIGID_MONGO_USER in second script 'backup.sh'
	b. mongodb 'password' and stores variable to ==> BIGID_MONGO_PWD in second script 'backup.sh'
	c. checks if SSL is enabled and stores varible to ==> SSL_TRUE in second script 'backup.sh'
	d. if SSL is true, CA.pem and SERVER.pem filenames are asked and stores variable to ==>CA_PEM and SERVER_PEM in second script 'backup.sh'
	e. Finally, asks the user if they want to run the backup now

3. Second Script contains the required variables to execute the actual backup
4. Backup is run and crontab is setup to execute backup every Saturday at 6am.