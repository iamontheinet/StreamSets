#!/bin/sh

## Set these variables
SCH_URL=<YOUR CONTROL HUB URL>
SCH_ORG=<YOUR ORG> 
SCH_USER=<YOUR USER>
SCH_PASSWORD=<YOUR PASSWORD> 
KUBE_NAMESPACE=streamsets
GKE_CLUSTER_NAME=<YOUR GKE CLUSTER NAME>
GCP_PROJECT_NAME=<YOUR GCP PROJECT NAME>
GCP_ZONE=<YOUR GCP ZONE>

## Update kubectl config with connection info
gcloud container clusters get-credentials ${GKE_CLUSTER_NAME} --zone ${GCP_ZONE} --project ${GCP_PROJECT_NAME}

## Create Namespace
kubectl create namespace ${KUBE_NAMESPACE}

## Set Context
kubectl config set-context $(kubectl config current-context) --namespace=${KUBE_NAMESPACE}

## Get gloud user
GCP_IAM_USERNAME=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")

## Create a service account to run the agent
kubectl create serviceaccount streamsets-agent --namespace=${KUBE_NAMESPACE}

## Get admin role in order to have RBAC permissions
kubectl create clusterrolebinding cluster-admin-binding \
    --clusterrole=cluster-admin \
    --user="$GCP_IAM_USERNAME"

## Create a role for the service account with permissions to 
## create pods (among other things)
kubectl create role streamsets-agent \
 --verb=get,list,create,update,delete,patch \
 --resource=pods,secrets,replicasets,deployments,ingresses,services,horizontalpodautoscalers \
 --namespace=${KUBE_NAMESPACE}
    
## Bind the role to the service account
kubectl create rolebinding streamsets-agent \
 --role=streamsets-agent \
 --serviceaccount=${KUBE_NAMESPACE}:streamsets-agent \
 --namespace=${KUBE_NAMESPACE}


## Get auth token fron Control Hub
SCH_TOKEN=$(curl -s -X POST -d "{\"userName\":\"${SCH_USER}\", \"password\": \"${SCH_PASSWORD}\"}" ${SCH_URL}/security/public-rest/v1/authentication/login --header "Content-Type:application/json" --header "X-Requested-By:SDC" -c - | sed -n '/SS-SSO-LOGIN/p' | perl -lane 'print $F[$#F]')

## Use the auth token to get a registration token for a Control Agent
AGENT_TOKEN=$(curl -s -X PUT -d "{\"organization\": \"${SCH_ORG}\", \"componentType\" : \"provisioning-agent\", \"numberOfComponents\" : 1, \"active\" : true}" ${SCH_URL}/security/rest/v1/organization/${SCH_ORG}/components --header "Content-Type:application/json" --header "X-Requested-By:SDC" --header "X-SS-REST-CALL:true" --header "X-SS-User-Auth-Token:${SCH_TOKEN}" | jq '.[0].fullAuthToken')

if [ -z "$AGENT_TOKEN" ]; then
  echo "Failed to generate control agent token."
  echo "Please verify you have Provisioning Operator permissions in SCH"
  exit 1
fi

## Store the agent token in a secret
kubectl create secret generic sch-agent-creds \
    --from-literal=dpm_agent_token_string=${AGENT_TOKEN}

## create a secret for control agent to use
kubectl create secret generic compsecret

## Generate a UUID for the agent
agent_id=$(uuidgen)
echo ${agent_id} > agent.id

## Store connection properties in a configmap for the agent
kubectl create configmap streamsets-config \
    --from-literal=org=${SCH_ORG} \
    --from-literal=sch_url=${SCH_URL} \
    --from-literal=agent_id=${agent_id}

## Deploy the control agent
kubectl create -f control-agent.yaml

temp_agent_Id=""
while [ -z $temp_agent_Id ]; do
  sleep 10
  temp_agent_Id=$(curl -L "${SCH_URL}/provisioning/rest/v1/dpmAgents?organization=${SCH_ORG}" --header "Content-Type:application/json" --header "X-Requested-By:SDC" --header "X-SS-REST-CALL:true" --header "X-SS-User-Auth-Token:${SCH_TOKEN}" | jq -r "map(select(any(.id; contains(\"${agent_id}\")))|.id)[]")
done
echo "DPM Agent \"${temp_agent_Id}\" successfully registered with SCH"

