from libs.modules.components import ScheduledTasks
from .domain_checker import scheduled_tasks as domain_checker
from .maintenance import scheduled_tasks as maintenance
from .proxy_change import scheduled_tasks as proxy_change
from .dns_checker import scheduled_tasks as dns_checker


scheduled_tasks = ScheduledTasks()
scheduled_tasks.extend(domain_checker._tasks)
scheduled_tasks.extend(maintenance._tasks)
scheduled_tasks.extend(proxy_change._tasks)
scheduled_tasks.extend(dns_checker._tasks)
