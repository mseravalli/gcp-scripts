import googleapiclient.discovery
import time

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-python.json

# compute = googleapiclient.discovery.build('compute', 'v1')
# instances = compute.instances().list(project=project, zone=zone).execute()
# instances_name = [i['name'] for i in instances['items']]
# print(instances_name)

project = "test-seravalli-199408"
region = "europe-west1"
zone = region+"-c"

disk_type = "pd-standard"

attached_disk_name_1=f"google-{disk_type}-{int(time.time()*1E7)}"
attached_disk_name_2=f"google-{disk_type}-{int(time.time()*1E7)}"

original_vm_name = f"original-vm-{int(time.time()*1E7)}"


compute = googleapiclient.discovery.build('compute', 'v1')
op = compute.projects().get(project="sandbox-303kdn50").execute()
# print(op)

crm = googleapiclient.discovery.build('cloudresourcemanager', 'v1')

project_body = {
      'name': 'test-sdf924hdjhg349h2ldkv',
      'project_id': 'test-sdf924hdjhg349h2ldkv',
      'parent': {
          'type': 'organization',
          'id': '1033877253515'
      }
}

request = crm.projects().delete(projectId="test-sdf924hdjhg349h2ldkv")
# request = crm.projects().create(body=project_body)
response = request.execute()


