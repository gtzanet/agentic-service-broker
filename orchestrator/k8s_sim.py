import random
import uuid
import time
from typing import Dict, List, Optional

class Pod:
    def __init__(self, service_name: str, cpu_request: float, memory_request: float):
        self.id = str(uuid.uuid4())[:8]
        self.service_name = service_name
        self.cpu_request = cpu_request
        self.memory_request = memory_request
        self.node_id: Optional[str] = None
        self.status = "Pending"

    def __repr__(self):
        return f"<Pod {self.id} ({self.service_name}) on {self.node_id}>"

class Node:
    def __init__(self, name: str, cpu_capacity: float, memory_capacity: float):
        self.name = name
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.pods: Dict[str, Pod] = {}

    @property
    def cpu_usage(self) -> float:
        return sum(p.cpu_request for p in self.pods.values())

    @property
    def memory_usage(self) -> float:
        return sum(p.memory_request for p in self.pods.values())

    def add_pod(self, pod: Pod) -> bool:
        if self.cpu_usage + pod.cpu_request > self.cpu_capacity:
            return False
        if self.memory_usage + pod.memory_request > self.memory_capacity:
            return False
        self.pods[pod.id] = pod
        pod.node_id = self.name
        pod.status = "Running"
        return True

    def remove_pod(self, pod_id: str) -> Optional[Pod]:
        if pod_id in self.pods:
            pod = self.pods.pop(pod_id)
            pod.node_id = None
            pod.status = "Pending"
            return pod
        return None

    def __repr__(self):
        return f"<Node {self.name} CPU:{self.cpu_usage}/{self.cpu_capacity}>"

class Service:
    def __init__(self, name: str, cpu_request: float, memory_request: float):
        self.name = name
        self.cpu_request = cpu_request
        self.memory_request = memory_request
        self.pods: Dict[str, Pod] = {}

class Cluster:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.services: Dict[str, Service] = {}

    def add_node(self, name: str, cpu_capacity: float, memory_capacity: float):
        self.nodes[name] = Node(name, cpu_capacity, memory_capacity)

    def deploy_service(self, name: str, replicas: int, cpu_request: float, memory_request: float):
        service = Service(name, cpu_request, memory_request)
        self.services[name] = service
        self.scale_service(name, replicas)

    def scale_service(self, service_name: str, replicas: int):
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not found")
        
        service = self.services[service_name]
        current_count = len(service.pods)
        
        if replicas > current_count:
            # Scale up
            for _ in range(replicas - current_count):
                pod = Pod(service_name, service.cpu_request, service.memory_request)
                service.pods[pod.id] = pod
                self._schedule_pod(pod)
        elif replicas < current_count:
            # Scale down
            pods_to_remove = list(service.pods.keys())[:current_count - replicas]
            for pod_id in pods_to_remove:
                pod = service.pods.pop(pod_id)
                if pod.node_id and pod.node_id in self.nodes:
                    self.nodes[pod.node_id].remove_pod(pod.id)

    def _schedule_pod(self, pod: Pod) -> bool:
        # Simple scheduler: find first node with capacity
        # Sort nodes by available CPU to balance slightly or pack? Let's just iterate.
        for node in self.nodes.values():
            if node.add_pod(pod):
                return True
        print(f"Warning: Could not schedule pod {pod.id} (insufficient capacity)")
        return False

    def move_pod(self, pod_id: str, target_node_name: str):
        # Find the pod
        pod = None
        source_node = None
        
        for node in self.nodes.values():
            if pod_id in node.pods:
                source_node = node
                pod = node.pods[pod_id]
                break
        
        if not pod:
            raise ValueError(f"Pod {pod_id} not found")
            
        if target_node_name not in self.nodes:
            raise ValueError(f"Target node {target_node_name} not found")
            
        target_node = self.nodes[target_node_name]
        
        # Check capacity on target (optimistic check)
        if target_node.cpu_usage + pod.cpu_request > target_node.cpu_capacity:
             raise ValueError(f"Target node {target_node_name} has insufficient CPU")

        # Move
        source_node.remove_pod(pod_id)
        if not target_node.add_pod(pod):
            # Rollback if failed (shouldn't happen due to check above, but good practice)
            source_node.add_pod(pod)
            raise ValueError(f"Failed to move pod to {target_node_name}")

    def get_metrics(self) -> Dict:
        # Generate synthetic metrics
        metrics = {
            "timestamp": time.time(),
            "nodes": {},
            "services": {}
        }
        
        total_cpu_usage = 0
        total_cpu_cap = 0
        
        for node_name, node in self.nodes.items():
            cpu_util = node.cpu_usage / node.cpu_capacity if node.cpu_capacity > 0 else 0
            # Latency increases with load
            base_latency = 20  # ms
            load_factor = cpu_util * 100 # extra ms based on load
            latency = base_latency + load_factor + random.uniform(-5, 5)
            
            metrics["nodes"][node_name] = {
                "cpu_usage": node.cpu_usage,
                "cpu_capacity": node.cpu_capacity,
                "cpu_utilization_pct": cpu_util * 100,
                "memory_usage": node.memory_usage,
                "pod_count": len(node.pods),
                "latency_ms": latency
            }
            total_cpu_usage += node.cpu_usage
            total_cpu_cap += node.cpu_capacity

        for svc_name, svc in self.services.items():
            # Service latency is avg of its pods' node latencies
            svc_latencies = []
            running_pods = 0
            for pod in svc.pods.values():
                if pod.node_id:
                    running_pods += 1
                    node_metric = metrics["nodes"][pod.node_id]
                    svc_latencies.append(node_metric["latency_ms"])
            
            avg_latency = sum(svc_latencies) / len(svc_latencies) if svc_latencies else 0
            
            # Request completion rate (synthetic)
            # Higher load -> lower completion rate? Or just random variation around a baseline.
            req_rate = 100 - (avg_latency / 5) # Simple inverse relationship
            
            metrics["services"][svc_name] = {
                "pod_count": len(svc.pods),
                "running_pods": running_pods,
                "avg_latency_ms": avg_latency,
                "request_completion_rate": max(0, req_rate)
            }
            
        metrics["cluster"] = {
            "total_nodes": len(self.nodes),
            "total_pods": sum(len(n.pods) for n in self.nodes.values()),
            "overall_cpu_utilization_pct": (total_cpu_usage / total_cpu_cap * 100) if total_cpu_cap > 0 else 0
        }
        
        return metrics
