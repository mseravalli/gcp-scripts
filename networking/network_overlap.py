#!/usr/bin/env python3

import time
import re
from absl import app
from absl import flags
import googleapiclient.discovery

# How to run:
# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/{service_account_credential}.json
# $ ./network_overlap.py --project_id=sandbox-303kdn50 

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id",
                    None,
                    "Project id that needs to be changed.")
flags.mark_flag_as_required("project_id")

def get_regions(project_id, compute):
  ''' returns [] of all regions in the project '''
  regions_raw = compute.regions().list(project=project_id).execute()
  return [r["name"] for r in regions_raw["items"]]

def get_cidr_ranges(project_id, compute):
  ''' returns [(range_name, cidr)] from all regions in the project '''
  regions = get_regions(project_id, compute)

  cidr_ranges = [] 
  for region in regions:
    subnets = compute.subnetworks().list(project=project_id, region=region).execute()
    for subnet in subnets["items"]:
      cidr_ranges.append((subnet["name"], subnet["ipCidrRange"]))
      if "secondaryIpRanges" in subnet:
        for r in subnet["secondaryIpRanges"]:
          cidr_ranges.append((subnet["name"], r["ipCidrRange"]))
  return cidr_ranges

def cidr_to_address(cidr):
  ''' returns (subnet_name, cidr, bin(address), mask) '''
  address = 0
  mask = int(cidr[1][cidr[1].index("/") + 1:])
  res = re.match(r"([0-9]+).([0-9]+).([0-9]+).([0-9]+)", cidr[1])
  address += int(res.groups()[3])
  address += (int(res.groups()[2]) << 8)
  address += (int(res.groups()[1]) << 16)
  address += (int(res.groups()[0]) << 24)
  return (cidr[0], cidr[1], address, mask)

def compare_cidr(cidr_ranges):
  ''' returns [(address1, address2)] '''
  addresses = [cidr_to_address(r) for r in cidr_ranges]
  same_addresses = []
  for i in range(len(addresses)):
    for j in range(i + 1, len(addresses)):
      mask = min(addresses[i][3], addresses[j][3])
      
      if (addresses[i][2] >> (32 - mask)) == (addresses[j][2] >> (32 - mask)):
        same_addresses.append((addresses[i], addresses[j]))

  return same_addresses

def main(argv):
  del argv # unused
  
  project_id = FLAGS.project_id
  compute = googleapiclient.discovery.build("compute", "v1")
  cidr_ranges = get_cidr_ranges(project_id, compute)
  matches = compare_cidr(cidr_ranges)
  if len(matches) > 0:
    print("matches:")
    for match in matches:
      print(match)
  else:
    print("no matches")

if __name__ == "__main__":
  app.run(main)
    
