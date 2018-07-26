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

# flags.mark_flag_as_required("project_ids")
# flags.mark_flag_as_required("zones")
 
# TODO: better parametrisation 
project = "test-seravalli-199408"
region = "europe-west1"
zone = region+"-c"
disk_type = "pd-standard"
attached_disk_name_1=f"google-{disk_type}-{int(time.time()*1E7)}"
attached_disk_name_2=f"google-{disk_type}-{int(time.time()*1E7)}"

compute = googleapiclient.discovery.build('compute', 'v1')

def wait_for_operation(compute, project, operation, region=None, zone=None):
  while True:
    result = None
    if zone is not None:
      result = compute.zoneOperations() \
        .get( project=project, zone=zone, operation=operation) \
        .execute()
    elif region is not None:
      result = compute.regionOperations() \
        .get( project=project, region=region, operation=operation) \
        .execute()
    else:
      result = compute.globalOperations() \
        .get( project=project, operation=operation) \
        .execute()
      
    if result['status'] == 'DONE':
      if 'error' in result:
        raise Exception(result['error'])
      return result
    time.sleep(1)

def create_static_ip(compute, project, region, subnet, ip_address):
  ip_name = f"static-ip-{ip_address.replace('.', '-')}"
  ip_body = {
    "name": ip_name,
    "addressType": "INTERNAL",
    "ipVersion": "IPV4",
    "address": ip_address,
    "subnetwork": f"regions/{region}/subnetworks/default", 
  }
  op = compute.addresses() \
    .insert(project=project, region=region, body=ip_body) \
    .execute()

  wait_for_operation(
    compute=compute,
    project=project,
    region=region,
    operation=op["name"]
  )

  ip_resource = compute.addresses() \
    .get(project=project, region=region, address=ip_name) \
    .execute()

  return ip_resource["selfLink"]
  
def create_vm(original_vm_name):
  original_vm_config = {
    "name": original_vm_name,
    "zone": zone,
    "machineType": f"zones/{zone}/machineTypes/n1-standard-4",
    "networkInterfaces": [ 
      { 
        "network": "global/networks/default",
        "subnetwork": f"regions/{region}/subnetworks/default", 
        "accessConfigs": [ 
          {
            "name": "External NAT",
            "type": "ONE_TO_ONE_NAT",
          },
        ],
      },
    ],
    "disks": [
      { 
        "deviceName": f"os-disk-{original_vm_name}",
        "initializeParams": {
          "diskName": f"os-disk-{original_vm_name}",
          "diskType": f"zones/{zone}/diskTypes/{disk_type}",
          "diskSizeGb": "20", 
          "sourceImage": "projects/debian-cloud/global/images/family/debian-8",
        },
        "autoDelete": True,
        "boot": True,
        "mode": "READ_WRITE",
        "type": "PERSISTENT", 
      },
      { 
        "deviceName": attached_disk_name_1,
        "initializeParams": {
          "diskName": attached_disk_name_1,
          "diskType": f"zones/{zone}/diskTypes/{disk_type}",
          "diskSizeGb": "20", 
        },
        "autoDelete": True,
        "boot": False,
        "mode": "READ_WRITE",
        "type": "PERSISTENT", 
      },
      { 
        "deviceName": attached_disk_name_2,
        "initializeParams": {
          "diskName": attached_disk_name_2,
          "diskType": f"zones/{zone}/diskTypes/{disk_type}",
          "diskSizeGb": "20", 
        },
        "autoDelete": True,
        "boot": False,
        "mode": "READ_WRITE",
        "type": "PERSISTENT", 
      },
    ],
    "metadata": { 
      "items": [
        {
          "key": "startup-script",
          "value": f"""#! /bin/bash
            yes | sudo mkfs.ext3 /dev/disk/by-id/{attached_disk_name_1}
            sudo mkdir -p /mnt/disks/{attached_disk_name_1}
            sudo mount /dev/disk/by-id/{attached_disk_name_1} \
              /mnt/disks/{attached_disk_name_1}
            sudo chmod 777 -R /mnt/disks/{attached_disk_name_1}
            echo 'hello' > /mnt/disks/{attached_disk_name_1}/hello1.txt

            yes | sudo mkfs.ext3 /dev/disk/by-id/{attached_disk_name_2}
            sudo mkdir -p /mnt/disks/{attached_disk_name_2}
            sudo mount /dev/disk/by-id/{attached_disk_name_2} \
              /mnt/disks/{attached_disk_name_2}
            sudo chmod 777 -R /mnt/disks/{attached_disk_name_2}
            echo 'hello' > /mnt/disks/{attached_disk_name_2}/hello2.txt
          """
        },
      ],
    },
  }

  compute = googleapiclient.discovery.build('compute', 'v1')
  op = compute.instances() \
    .insert(project=project, zone=zone, body=original_vm_config) \
    .execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print("vm created")

def clone_vm_w_static_ip(original_vm_name):
  original_vm = compute.instances() \
    .get(project=project, zone=zone, instance=original_vm_name) \
    .execute()

  # copy original settings
  cloned_vm_type = original_vm["machineType"]
  cloned_vm_zone = original_vm["zone"]
  cloned_vm_ip = original_vm["networkInterfaces"][0]["networkIP"]
  cloned_vm_subnetwork = original_vm["networkInterfaces"][0]["subnetwork"]
  cloned_vm_attached_disks = [d for d in original_vm["disks"] if not d["boot"]]
  cloned_vm_boot_disk = [d for d in original_vm["disks"] if d["boot"]][0]

  # disable disks deletion at VM deletion
  for d in original_vm["disks"]:
    op = compute.instances() \
      .setDiskAutoDelete(project=project,
                         zone=zone,
                         instance=original_vm_name,
                         autoDelete=False,
                         deviceName=d["deviceName"]) \
      .execute()
    wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

  print("vm setting copied")

  op = compute.instances().delete(project=project, zone=zone, instance=original_vm_name).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print("vm deleted")

  # create_new ip TODO
  cloned_vm_ip_url = create_static_ip(
    compute=compute,
    project=project,
    region=region,
    subnet="",
    ip_address=cloned_vm_ip
  )
  print("address created")

  cloned_vm_startup_script="""#! /bin/bash"""
  for d in cloned_vm_attached_disks:
    cloned_vm_startup_script=f"""{cloned_vm_startup_script} 
      sudo mkdir -p /mnt/disks/{d['deviceName']} ;
      sudo mount /dev/disk/by-id/{d['deviceName']} /mnt/disks/{d['deviceName']}
      sudo chmod 777 -R /mnt/disks/{d['deviceName']} ;
    """

  cloned_vm_config = {
    "name": original_vm_name + "-w-static",
    "zone": zone,
    "machineType": cloned_vm_type[cloned_vm_type.rfind("zones"):],
    "networkInterfaces": [ 
      { 
        "network": "global/networks/default",
        "subnetwork": f"regions/{region}/subnetworks/default", 
        "networkIP": cloned_vm_ip_url,
        "accessConfigs": [ 
          {
            "name": "External NAT",
            "type": "ONE_TO_ONE_NAT",
          },
        ],
      },
    ],
    "disks": original_vm["disks"],
    "metadata": { 
      "items": [
        {
          "key": "startup-script",
          "value": cloned_vm_startup_script
        },
      ],
    },
  }

  op = compute.instances().insert(project=project, zone=zone, body=cloned_vm_config).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print("vm cloned")

def main():
  FLAGS = flags.FLAGS
  FLAGS(sys.argv)

  vm_name = f"vm-{int(time.time()*1E7)}"
  create_vm(vm_name)
  clone_vm_w_static_ip(vm_name)

if __name__ == "__main__":
    main()

