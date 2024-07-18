from core.utils.module.components import EventManager
from .dns_cheker import event_consumers as dns_consumers
from .domain_check import event_consumers as domain_consumers

event_consumers = EventManager()
event_consumers.extend(dns_consumers.events)
event_consumers.extend(domain_consumers.events)
