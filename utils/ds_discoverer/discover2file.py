"""Scan network and create data sources file."""
import os
import subprocess
from xml.dom import minidom
import csv

IP_RANGE = os.environ['DISCOVERER_IP_RANGE']
SCAN_TYPE = os.environ['DISCOVERER_SCAN_TYPE']
# e.g. https://localhost/api/v1


# def create_header():
#    """Create file header."""
#     global discovery_writer
#    with open('discovery.csv', mode='w') as discovery_file:
#        discovery_writer = csv.writer(discovery_file, delimiter=',',
#                                     quotechar='"', quoting=csv.QUOTE_MINIMAL)
#
#        discovery_writer.writerow(['name', 'credential_id', 'security_tier',
#                                   'rdb_is_sample_data', 'rdb_url', 'type',
#                                   'scanner_strategy', 'enabled',
#                                   'differential', 'is_credential'])
#

def create_row(name, address, type, sharedResource):
    """Create file entry."""
    with open('discovery.csv', mode='a') as discovery_file:
        discovery_writer = csv.writer(discovery_file, delimiter=',',
                                      quotechar='"', quoting=csv.QUOTE_MINIMAL)

        discovery_writer.writerow([name, type, "1", "true", address, type,
                                  "SCAN_ALL", "yes", "false", "true",
                                   sharedResource])


def scan_cmd(SCAN_TYPE):
    """Get the scan command for each scan type."""
    scanDict = {
      "rdb": subprocess.run(["nmap", "-p", "T:1433-1433,T:3306,T:5432,T:1521",
                             "-sV", IP_RANGE, "--open",
                             "-oX", "nmap_output.xml"]),
      "smb": subprocess.run(["nmap", "-sS", "--script", "smb-enum-shares.nse",
                             "-p", "T:139, T:445", IP_RANGE, "--open",
                             "-oX", "nmap_output.xml"]),
      "nfs": subprocess.run(["nmap", "-p", "T:2049", IP_RANGE, "--open", "-oX",
                             "nmap_output.xml"]),
    }
    data = str(scanDict.get(SCAN_TYPE))
    return data


def get_csv_data(service, address, port, name):
    """Prepare DS http body by Service Name."""
    address = address + ":" + port
    dsDict = {
       # MySQL DS request body
       "mysql": "rdb-mysql",
       "ms-sql-s": "rdb-mssql",
       "postgresql": "rdb-postgresql",
       "oracle-tns": "rdb-oracle",
       "mongodb": "mongodb",
       "microsoft-ds": "smb",
       "nfs": "nfs"
       }

    data = str(dsDict.get(service))
    return(data)


def xml_processor(file):
    """Process scan results and perform imports."""
    print("preparing scan results for import...")
    doc = minidom.parse(file)
    hosts = doc.getElementsByTagName("host")
    for host in hosts:
        address = host.getElementsByTagName("address")[0].getAttribute("addr")
        ports = host.getElementsByTagName("port")
        name, type, service = prep_ds_entry(address, ports)
        tables = host.getElementsByTagName("table")
        name, type, service = prep_ds_entry(address, ports)
        if name != "None":
            create_row(name, address, type, "")
        if tables != []:
            if SCAN_TYPE == "smb" or SCAN_TYPE == "meta":
                    if name is not None:
                        print("name:" + name)
                        for table in tables:
                            service, sharedResource = prep_smb_shares(
                                address, table)
                            create_row(service, address, type, sharedResource)


def prep_ds_entry(address, ports):
    """Get values for DS entries."""
    for prt in ports:
        port = prt.getAttribute("portid")
        if len(prt.getElementsByTagName("service")) > 0:
                service = (prt.getElementsByTagName("service")
                           [0].getAttribute("name"))
                name = "auto-discovered-" + service + "-" + address
                name = name.replace(".", "-")
                type = get_csv_data(service, address, port, name)
                if port is not None:
                    service = service + ":" + port
    return name, type, service


def prep_smb_shares(address, tbl):
    """Parse SMB shares and prepare http body for import."""
    # if tbl is not None:
    share = tbl.getAttribute("key")
    access = tbl.getElementsByTagName("elem")
    print(address)
    print("share:" + share)
    for desc in access:
            print("desc: " + desc.getAttribute("key"))
            print(share)
            share = share.split("\\")
            if len(share) > 2:
                service = ("auto-discovered-" + address +
                           "_"+share[3])
                service = service.replace(".", "-")
                service = service.replace("$", "_")
                return service, share[3]


def meta_scan(file):
        """Run a scan on all ports."""
        # scans are splitted in order to optimize performance.
        print("\nscanning all ports for all services")
        subprocess.run(["nmap", "-p-", IP_RANGE, "-sV", "--open", "-oX", file])
        xml_processor(file)
        print("\nscanning smb with open shares discovery")
        file = "smb_output.xml"
        smb_scan(file)
        xml_processor(file)
        # nfs servers are not discovered using the meta scan command
        print("\nscanning for nfs servers")
        file = "nfs_output.xml"
        nfs_scan(file)
        xml_processor(file)


def rdb_scan(file):
    """RDB Scan command."""
    subprocess.run(["nmap", "-p", "T:1433-1433,T:3306,T:5432,T:1521",
                    "-sV", IP_RANGE, "--open", "-oX", file])


def smb_scan(file):
    """SMB Scan command."""
    subprocess.run(["nmap", "-sS", "--script",
                    "smb-enum-shares.nse",
                    "-p", "T:139, T:445", IP_RANGE, "--open",
                    "-oX", file])


def nfs_scan(file):
    """NFS Scan command."""
    subprocess.run(["nmap", "-p", "T:2049", IP_RANGE, "--open", "-oX", file])


def main():
    """Flow starts here."""
    file = SCAN_TYPE + "_output.xml"

    with open('discovery.csv', mode='w') as discovery_file:
        discovery_writer = csv.writer(discovery_file, delimiter=',',
                                      quotechar='"',
                                      quoting=csv.QUOTE_MINIMAL)

        discovery_writer.writerow(['name', 'credential_id',
                                   'security_tier',
                                   'rdb_is_sample_data', 'rdb_url', 'type',
                                   'scanner_strategy', 'enabled',
                                   'differential', 'is_credential',
                                   'sharedResource'])

    if SCAN_TYPE != 'meta':
        scanDict = {
          # Get scan function by scan type.
          "rdb": "rdb_scan(file)",
          "smb": "smb_scan(file)",
          "nfs": "nfs_scan(file)"
        }
        print("Starting " + SCAN_TYPE + " scan." +
              " Results will be saved to nmap_output.xml")
        # Execute scan.
        exec(scanDict.get(SCAN_TYPE))
        print(file)

        xml_processor(file)
    else:
        meta_scan(file)
    print('\nDone. please check BigID for data source names ' +
          'which start with "auto-discovered"')


if __name__ == '__main__':
    main()
