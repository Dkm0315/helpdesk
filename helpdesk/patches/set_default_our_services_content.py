import frappe


DEFAULT_OUR_SERVICES_CONTENT = """# Our Services

We provide comprehensive support and managed services for open-source technologies. Our team handles deployment, monitoring, optimization, and troubleshooting so you can focus on building your product.

## Redis

We offer full lifecycle management for Redis instances including:

- **Deployment & Configuration** — Cluster setup, sentinel configuration, and performance tuning
- **Monitoring & Alerting** — Real-time metrics, memory usage tracking, and automated alerts
- **Backup & Recovery** — Scheduled snapshots, point-in-time recovery, and disaster recovery planning
- **Performance Optimization** — Key eviction policies, memory management, and query optimization

## Apache Kafka

End-to-end Kafka management covering:

- **Cluster Operations** — Broker provisioning, topic management, and partition rebalancing
- **Monitoring & Observability** — Consumer lag tracking, throughput metrics, and health dashboards
- **Schema Management** — Schema registry setup, compatibility checks, and evolution strategies
- **Security** — ACL configuration, encryption in transit, and authentication setup

## MongoDB

Complete MongoDB support including:

- **Deployment & Scaling** — Replica set configuration, sharding strategies, and capacity planning
- **Performance Tuning** — Index optimization, query profiling, and aggregation pipeline optimization
- **Backup & Restore** — Automated backups, oplog-based recovery, and cross-region replication
- **Security & Compliance** — Role-based access control, encryption at rest, and audit logging

---

*For additional technologies or custom service requirements, please reach out to our team.*"""


def execute():
	"""Set default Our Services content for existing installations."""
	settings = frappe.get_single("HD Settings")
	current = getattr(settings, "our_services_content", None)
	if not current:
		frappe.db.set_single_value(
			"HD Settings", "our_services_content", DEFAULT_OUR_SERVICES_CONTENT
		)
		frappe.db.commit()
