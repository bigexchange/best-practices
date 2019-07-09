# ds_discoverer

## Purpose:
scans the network for data sources and creates the data sources in BigID


## Limitations:

- meta scan type is work in progress. it currently maps rdb (ms-sql,mysql,postgress,oracle),nfs,smb and mongo.
  in case you need to dsiscover other DS types - please send me (Tal) an nmap output file, or do it your self by adding the suiteabler entry in the dsDict.

## Best Practice:
In case you are using a Network scan:
- Verify that the customer approves it.
- Start with  Network discovery to csv file in order to asses the amount of data sources in the network.

## Scan Methods and relevant scripts

#Network discovery to csv_file and import from csv to BigID
   script: run_discover2file.sh  
   description: run_discover2file.sh creates a csv file named discovery.csv with all discovered data sources and copies it to the Docker Host.  
   Environment variables:  
                DISCOVERER_IP_RANGE - The ip addresses range to scan. supports several formats. tested examples: 192.168.1.1-254 and 192.168.0/24  
                DISCOVERER_SCAN_TYPE - determines which data sources to search for. Allowed values: smb,rdb,nfs,meta  
                DISCOVERER_BIGID_API_URL - The BigID api endpoint. https://<bigid_server>/api/v1  
                DISCOVERER_BIGID_PWD - The bigid password  

   script: import_ds_from_file.sh  
   pre-requisites: a discoverer container created by run_discover2file.sh must be running  
   description: copies the discovery.csv file from the docker host to the container and imports the data sources from the file (created by discover2file.sh) to BigID using import_ds_from_file.sh  
                This allows you to double check and clean the file before potentially importing a mass ofdata sources to BigID.  


  # Note regarding  Network Discovery Scan Types
  - rdb, nfs and smb types scans only the default ports for each service.  
  - smb scan brings ALL DISCOVERED SMB SHARES.  
  - meta - scans all ports for servcices relevant for us (supported by our connectors) and updated in the dsDict dictionatry object.  
           when done, it runs an smb scan and an nfs scan.  

#Service Now DS import
   scripts: discover_sn.sh  
   description: imports ServiceNow configuration items from it's CMDB as BigID data sources.  





## General Notes:
This code is BigID community code and not officially supported.




## How to Set it up
--------------------
1. On the BigID docker host, build the Dodcker image
2. update the shell scripts  with your environment variables values.
  (the bigid url is the docker ip address of the docker host)
3. execute the relevant shell script
