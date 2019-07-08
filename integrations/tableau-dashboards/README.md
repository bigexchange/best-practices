# Purpose of this project
Provide Tableau dashboard examples for usage by BigID customers, partners and internal teams when they implement Tableau dashboards based on BigID data.

Feel free to contribute!

## Please note: 
The content of this project is not a part of the product and not officially supported.

## Best practices
1. Always clone to a branch - Never push to master!
1. When done, issue a pull request and add an admin and the original developer of the tool you are changing as reviewers.
1. Test your stuff and provide a readme.
1. Provide detailed installation or configuration instructions to make it easier to use your contributions.

# Customizations
To integrate Tableau with BigID, you can:

* Export relevant data from BigID as CSV or JSON files (e.g., the detailed scan results) which can then be imported into Tableau. This approach will not allow a “live” connection.
* Customize a web connector for Tableau that leverages the BigID API to pull relevant data dynamically. For this, you need to install the MongoDB BI Connector on top of MongoDB, and integrate Tableau directly with it. Also remember to use a read-only user, and only access tables that are safe.

## Installing MongoDB BI Connector

1. Download the relevant MongoDB BI Connector package relevant to your platform (Linux, MacOS or Windows).
1. Install the package following the platform-specific instructions at https://docs.mongodb.com/bi-connector/master/installation/.
    *  Some instructions also include steps to set mongosqld as a service and start at startup.
1. Create SSL keys and certificates following instructions at https://dev.mysql.com/doc/refman/5.7/en/creating-ssl-files-using-openssl.html.
    *  This is needed to enable SSL connection between Tableau and the BI Connector.
1. Create a new combined.pem file and merge the full content of server-key.pem and server-cert.pem into it.
1. The MongoDB BI Connector can be customized using command-line parameters, but it is easier to do so using a YAML configuration file.
1. Start from the example-mongosqld-config.yml template, modify as follows and save as mongosqld.yml:
```
net:
  bindIp: "0.0.0.0"
  port: 3307
  ssl:
    mode: "allowSSL"
    allowInvalidCertificates: true
    PEMKeyFile: /path/to/combined.pem
    CAFile: /path/to/ca.pem
mongodb:
  net:
    uri: "mongodb://<your MongoDB DNS name or IP address>:27017"
    ssl:
      enabled: false
    auth:
      username: <your MongoDB username>
      password: <your MongoDB password>
security:
  enabled: true
systemLog:
  path: '/path/to/logfile.log'
processManagement:
  service:
    name: "mongosql"
    displayName: "MongoSQL Service"
    description: "MongoSQL accesses MongoDB data with SQL"
```
7. Run as `sudo mongosqld --config=</path/to/mongosqld.yml>`
1. Load the desired dashboard to your Tableau Desktop.
1. Update the connection to the data source to match your system, using the same username defined earlier in mongosqld.yml (and its password).