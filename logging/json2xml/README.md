# Overview
In this folder it is possible to find an example for how to use Cloud Functions
to intercept alerts from Stackdriver and further process them. The Cloud
Fuction deployed accepts authenticated requests, converts the requests'
body from JSON to XML and forwards the newly created XML to a provided url.

# Setup
## Create the Cloud Function
First deploy the function, this can be done by running from the directory where
the funciton is stored

```
$ ./setup.sh
```

## Configure Stackdriver
Once that is done you need to set Stackdriver to use your cloud function for
reporting the alerts. To do this you first need to configure a webhook.

1. Open your Stackdriver account.
1. From the cascading menu on the top left select `Account Setting`
1. In the `Settings` pane select `Notifications`
1. On the top menu of the main window of the setting select `Webhooks`
1. Click on `Add Webhook`
   1. Endpoint URL: the url of your Cloud Function can be found using `gcloud`
       ```
      $ gcloud beta functions describe json2xml --region europe-west1 | grep httpsTrigger -A 1
      ```
   1. Enter a Webhook Name
   1. Select Basic Auth and insert
      * Auth Username: `john`
      * Auth Passwork: `secret`
   1. Test Connection
   1. Verify in the Cloud Function Logs that the request is received and
processed. The logs will contain 4 entries similar to the following ones
      ```
      D  json2xml 5vd2h696rc9b Function execution started json2xml
      I  json2xml 5vd2h696rc9b { version: 'test', incident: { incident_id: 'test' } }
      I  json2xml 5vd2h696rc9b <version>test</version> <incident> <incident_id>test</incident_id> </incident> 
      D  json2xml 5vd2h696rc9b Function execution took 9 ms, finished with status code: 200 
      ```
   1. Save

Please remember to change the username and password to more secure ones for a
production environment.

# Testing
To validate the connection create a new Alert in Stackdriver and connect use the
previously created webhook as notification mechanism.

1. From the left menu select `Alerting` and from the sub-menu that pops up
`Create a Policy `
1. In the policy select a condition that will immediately trigger e.g. CPU usage
for any VM higher than 1% for 1 minute.
1. As notification select `Webhook` and the webhook name it was created in the
previous steps
1. Choose a name for your alert.
1. Wait for the alert to be triggered and check the logs of the Cloud Function
to ensure that the alert was correctly notified and processed.
