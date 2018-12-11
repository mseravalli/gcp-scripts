# SAP installation
This readme describes how it is possible to install SAP Hana and the related components.

## Prerequisites
In orer to be able to run the scripts present in this repository it is necessary to have Python 3.\* and Google Cloud SDK installed on the developers' workstation.

# SAP Hana
Hana will be setup using the standard scripts and templates provided by GCP.

## Setup
First update the file `setup.sh`. 
[TODO]: setup of setup.sh needs to be improved
Once the file is updated, it can be run:
```
$ ./setup.sh
```

### How does it work?
The script executes the Deployment Manager (DM) template sap-hana.py. The official version of this template can be found under `https://storage.googleapis.com/sapdeploy/dm-templates/sap_hana/sap_hana.py`.
However, for studying purposes the same files could be found in the directory `dm-templates`.
The template `sap-hana.py` creates the necessary infrastructure for hosting Hana and then executes the scripts `dm-templates/sap_hana/startup.sh` on the master node and `dm-templates/sap_hana/startup_secondary.sh` on the worker nodes.

# SAP Netweaver
## Setup

# SAP Operations
## Scale up
To run the scale up it is necessary to run the following command. 
```
$ scale_up.py
```
## Scale out
To run the scale up it is necessary to run the following command. 
```
$ scale_out.py
```
