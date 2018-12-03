from absl import flags
import googleapiclient.discovery
import time
import sys

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-python.json

flags.DEFINE_list("project_ids",
                  None,
                  "The IDs of the project that need to be checked")

flags.DEFINE_list("zones",
                  None,
                  "The IDs of the project that need to be checked")

flags.mark_flag_as_required("project_ids")
flags.mark_flag_as_required("zones")
 
compute = googleapiclient.discovery.build('compute', 'v1')

def get_zone(vm):
  return vm["zone"].split("/")[-1]

def get_type(vm):
  return vm["machineType"].split('/')[-1]

def get_consumption(project_ids, zones):
  results = [compute.instances().list(project=project_ids[0], zone=z).execute()
    for z in zones]
  vms = [vm for r in results for vm in r["items"]]
 

  print(vms)
  resources = [
    compute \
      .machineTypes() \
      .get(project=project_ids[0], zone=get_zone(vm), machineType=get_type(vm)) \
      .execute()
      for vm in vms]
 
  total_cpu = sum([r["guestCpus"] for r in resources])
  total_ram = sum([r["memoryMb"] for r in resources])/(1024**2)
  print(f"Total CPU: {total_cpu}")
  print(f"Total RAM: {total_ram} TB")

def main():
  FLAGS = flags.FLAGS
  FLAGS(sys.argv)
  get_consumption(project_ids = FLAGS.project_ids, zones = FLAGS.zones)

if __name__ == "__main__":
    main()

