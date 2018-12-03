export MASTER_IP=10.132.0.5
export SERVICE_CLUSTER_IP_RANGE="10.0.0.0/16"
export MASTER_CLUSTER_IP=10.0.0.1
export CLUSTER_NAME="k8scluster"
export CA_CERT="/srv/kubernetes/ca.crt"
export MASTER_CERT="/srv/kubernetes/server.crt"
export MASTER_KEY="/srv/kubernetes/server.key"


#kubeadm join 10.132.0.6:6443 --token oe3rsw.hza3wgqlus95vxg8 --discovery-token-ca-cert-hash sha256:6209ae93f18a01f06d257eef33526a2dda7b8083652062def72e6a707c08c1da

# gcloud compute scp instance-1532678088:pki/ca.crt .
# gcloud compute scp instance-1532678088:pki/ca.key .
# gcloud compute scp instance-1532678088:pki/sa.key .
# gcloud compute scp instance-1532678088:pki/sa.pub .
# gcloud compute scp instance-1532678088:pki/front-proxy-ca.crt .
# gcloud compute scp instance-1532678088:pki/front-proxy-ca.key .
# gcloud compute scp instance-1532678088:pki/etcd/ca.crt etcd-ca.crt
# gcloud compute scp instance-1532678088:pki/etcd/ca.key etcd-ca.key

gcloud compute scp ca.crt             instance-1532678201:ca.crt 
gcloud compute scp ca.key             instance-1532678201:ca.key 
gcloud compute scp sa.key             instance-1532678201:sa.key 
gcloud compute scp sa.pub             instance-1532678201:sa.pub 
gcloud compute scp front-proxy-ca.crt instance-1532678201:front-proxy-ca.crt 
gcloud compute scp front-proxy-ca.key instance-1532678201:front-proxy-ca.key 
gcloud compute scp etcd-ca.crt        instance-1532678201:etcd-ca.crt
gcloud compute scp etcd-ca.key        instance-1532678201:etcd-ca.key

gcloud compute scp ca.crt             instance-1532678103:ca.crt 
gcloud compute scp ca.key             instance-1532678103:ca.key 
gcloud compute scp sa.key             instance-1532678103:sa.key 
gcloud compute scp sa.pub             instance-1532678103:sa.pub 
gcloud compute scp front-proxy-ca.crt instance-1532678103:front-proxy-ca.crt 
gcloud compute scp front-proxy-ca.key instance-1532678103:front-proxy-ca.key 
gcloud compute scp etcd-ca.crt        instance-1532678103:etcd-ca.crt
gcloud compute scp etcd-ca.key        instance-1532678103:etcd-ca.key
