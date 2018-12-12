# SAP installation
This readme describes how it is possible to install SAP Hana and the related components.

## Prerequisites
In orer to be able to run the scripts present in this repository it is necessary to have Google Cloud SDK installed on the developers' workstation.

# SAP Hana
Hana will be setup using the standard scripts and templates provided by GCP.

## Setup
First update the file `setup.sh`. 
In `setup.sh`, the variables at the beginning of the file need to be updated with the values of the current environment.
```
PROJECT=""
INSTANCE_NAME=""
NETWORK_NAME=""
SUBNET=""
ZONE=""
TAG=""
```
Once the file is updated, it can be run, by executing:
```
$ ./setup.sh
```

### How does it work?
The script executes the Deployment Manager (DM) template sap-hana.py. The official version of this template can be found under `https://storage.googleapis.com/sapdeploy/dm-templates/sap_hana/sap_hana.py`.
However, for customization purposes the same files could be found in the directory `dm-templates`.
The template `sap-hana.py` creates the necessary infrastructure for hosting Hana and then executes the scripts `dm-templates/sap_hana/startup.sh` on the master node and `dm-templates/sap_hana/startup_secondary.sh` on the worker nodes.

# SAP Operations

## Prerequisites

### Python

The scripts for the operations are running using python 3.6 and using the Google Client APIs.
In order to setup such an environment it is necessary to install python 3.6 first and then installing the necessary dependencies.

The python dependencies can be installed by running:
```
$ pip3 install --upgrade google-api-python-client
```

More information can be found [here](https://developers.google.com/api-client-library/python/start/installation).

### Service Account

The script will be run as a service account. It is hence necessary to:

* setup a service account.
* download the respective credentials in JSON format.
* export the location of the credentials so that they are usable from the script.
  ```
    $ export GOOGLE_APPLICATION_CREDENTIALS=full_path_of_service_account_credentials
  ```

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
