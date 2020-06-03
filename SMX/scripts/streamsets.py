import requests
import json
import sys
import random
import time
import uuid
from elasticsearch import Elasticsearch
es = Elasticsearch(["http://34.214.19.5:9200"])

def sdc_executor_metrics(auth_token, sdc_label, test=False):

  print("Retrieving metrics for executor label: %s" % sdc_label)
  rest_api_url = "https://trailer.streamsetscloud.com/jobrunner/rest/v1/metrics/executors?label="+sdc_label

  api_response = requests.get(rest_api_url, headers={"X-SS-User-Auth-Token": auth_token, "X-Requested-By":"Dash-SMX", "Content-Type": "application/json"})
  json_paylod  = json.loads(api_response.text)

  # {'totalCount': 1, 'offset': 0, 'len': -1, 'data': 
  # [{'id': '786fb637-9cb2-11ea-ba4b-b58d186cc1ff', 'organization': 'iamontheinet', 'httpUrl': 'https://172.31.34.23:18631', 
  # 'version': '3.16.0', 'labels': [], 'reportedLabels': ['3.16-GA'], 'pipelinesCommitted': [], 'lastReportedTime': 1590735613073, 
  # 'startUpTime': 1590510090336, 'offsetProtocolVersion': 2, 'edge': False, 'cpuLoad': 5.1046931407942235, 'totalMemory': 1037959168.0, 
  # 'usedMemory': 580431240.0, 'pipelinesCount': 4, 'responding': True, 'idSeparator': '__', 'executorType': 'COLLECTOR', 'maxCpuLoad': 100.0, 
  # 'maxMemoryUsed': 100.0, 'maxPipelinesRunning': 1000000}]}

  epoch = json_paylod["data"][0]["lastReportedTime"]
  # print(epoch)
  timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch / 1000))
  # print(timestamp)
  json_paylod["data"][0]["lastReportedTime_ts"] = timestamp

  # print(json_paylod)

  print(json_paylod["data"][0])

  # print(res['result'])
  print("=====")

  if (test == True):
    print("^^^ this is a test! not writing to the destination!")
  else:
    res = es.index(index="sdc_executor_metrics", id=uuid.uuid4(), body=json_paylod["data"][0])


def main():
  # print(sys.argv[1])
  total_requests = int(sys.argv[1])

  if (total_requests > 0):
    creds = {"userName":"admin@iamontheinet", "password": "Dishdash123!"}
    auth = requests.post('https://trailer.streamsetscloud.com/security/public-rest/v1/authentication/login', data=json.dumps(creds), headers={"X-Requested-By":"Alexa","Content-Type": "application/json"})
    auth_token = auth.cookies['SS-SSO-LOGIN']
    index_name = "sdc_executor_metrics"   

    # print("***** auth token: %s" % auth_token)

    if len(sys.argv) >= 3:
      sdc_label = sys.argv[2]
    else:
      sdc_label = "3.16-GA"

    # if es.indices.exists(index_name):
    #   es.indices.delete(index=index_name)

    settings = {
      "mappings": {
          "properties": {
              "lastReportedTime": {
                  "type":"date"
              }
          }
       }
    }

    # create index
    es.indices.create(index=index_name, ignore=400, body=settings)

    is_test = True

    for cnt in range(1,total_requests+1):
      print("===== Sending executor metrics for %s to Elasticsearch (%s of %s) =====" % (sdc_label, cnt, total_requests))
      sdc_executor_metrics(auth_token, sdc_label)
      # time.sleep(2)


if __name__ == "__main__":
    main()
