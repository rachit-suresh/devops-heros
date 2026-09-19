# Session 11 - Kubernetes Services

**Name:** Rachit S
**Roll No:** 24BCS10139

## Environment

My laptop is not working, so I ran this lab on a cloud VM (GitHub Codespace) with minikube v1.39.0 (docker driver), Kubernetes v1.37.0. Two environment quirks matter for honesty below:

- The minikube node has no outbound internet at all (DNS and TCP egress are blocked by the sandboxed VM network). Images were pulled on the host and loaded into the node with `minikube image load`.
- Pod DNS (CoreDNS) was fixed to forward through a small DNS relay on the VM host, which is how the ExternalName resolution below could work.

Full raw log: `evidence/session-11.log`. Screenshots are terminal captures rendered from that log.

## 01 - ClusterIP

The default service type: a stable virtual IP reachable only inside the cluster. I deployed the app, created the ClusterIP service, and from a client pod curled the service name - DNS resolved `web-service-clusterip` to its ClusterIP and the request was load-balanced across the backend pods. This is the workhorse for internal east-west traffic: pods come and go, the ClusterIP and DNS name stay.

Screenshot: `Screenshots/s11-1-clusterip.png`

## 02 - NodePort

Opens the same static port on every node (here 30xxx) and forwards to the pods. I curled `http://$(minikube ip):<nodeport>` from the VM host and got the app response. NodePort is how you reach a service from outside without a cloud load balancer - and under the hood a NodePort service also gets a ClusterIP.

Screenshot: `Screenshots/s11-2-nodeport-lb.png` (top half)

## 03 - LoadBalancer

On a cloud provider this type provisions a real external load balancer and fills in EXTERNAL-IP. On minikube the service is created fine but EXTERNAL-IP stays `<pending>` because there is no cloud controller to fulfill it. I started `minikube tunnel` (the minikube shim that pretends to be a load balancer); in this docker-driver-on-a-VM setup the IP still stayed pending, which I left in the log as-is. The concept is still demonstrated by the manifest and behavior: LoadBalancer = NodePort + cloud provider integration, and without a provider it degrades to pending.

Screenshot: `Screenshots/s11-2-nodeport-lb.png` (bottom half)

## 04 - ExternalName

No selectors, no pods, no ClusterIP - the service is purely a DNS CNAME that CoreDNS returns. The teacher's manifest maps `external-database-service` to `nencyravaliya.me`.

My nslookup from the test pod shows exactly the expected mechanism:

```
external-database-service.default.svc.cluster.local  canonical name = nencyravaliya.me
```

Two honest caveats, both visible in the log:

- The teacher's target domain `nencyravaliya.me` currently has no live DNS record (NXDOMAIN - verified from the VM host too, not just inside the cluster), so the CNAME target itself cannot resolve further today.
- This environment blocks pod TCP egress, so an actual HTTP request through the alias cannot leave the cluster here.

To prove the mechanism end-to-end I added one supplementary check of my own (clearly marked in the log): an identical ExternalName pointing at `example.com`, which resolved through CoreDNS to real A and AAAA addresses. Same mechanism, live target.

Screenshot: `Screenshots/s11-3-externalname.png`

## 05 - Headless Service

`clusterIP: None` means no virtual IP and no kube-proxy load balancing: DNS returns the pod IPs directly. With the StatefulSet, `nslookup web-service-headless` returned all pod IPs, and `web-stateful-0.web-service-headless` resolved to one specific pod - that per-pod DNS record is why headless services pair with StatefulSets (databases, queues) where clients must address individual members. I also curled a specific pod through its stable DNS name.

Screenshot: `Screenshots/s11-4-headless.png`

## Troubleshooting - the empty endpoints bug

The teacher's broken manifest creates `broken-backend-service` with selector `app=wrong-backend-name`. `kubectl get endpoints` showed `<none>` - the service exists but routes to nothing. `kubectl describe svc` exposes the cause: the selector matches no pod labels. A service is only a selector over live pods; when endpoints are empty, the selector/label mismatch is almost always the bug. Fixing the selector (or the pod labels) repopulates endpoints.

Screenshot: `Screenshots/s11-5-empty-endpoints.png`

## Takeaway

Service type is about WHO should reach the pods: ClusterIP for internal traffic, NodePort for dev/external access without a cloud, LoadBalancer for production cloud exposure, ExternalName for aliasing outside systems, headless for direct per-pod addressing. And `kubectl get endpoints` is the first command to run whenever a service "doesn't work".
