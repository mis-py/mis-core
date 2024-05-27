from libs.modules.components import ScheduledTasks
from modules.binom_companion.tasks import domain_checker, maintenance, proxy_change
from modules.binom_companion.consumers import dns_cheker

scheduled_tasks = ScheduledTasks()
scheduled_tasks.extend(domain_checker.scheduled_tasks._tasks)
scheduled_tasks.extend(maintenance.scheduled_tasks._tasks)
scheduled_tasks.extend(proxy_change.scheduled_tasks._tasks)

