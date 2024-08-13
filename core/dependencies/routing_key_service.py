from core.repositories.routing_key import RoutingKeyRepository
from core.repositories.routing_key_subscription import RoutingKeySubscriptionRepository
from core.services.notification import RoutingKeyService, RoutingKeySubscriptionService, Notificator
from libs.ws_manager import WSManager


# Put it to separate file to prevent from circular imports
def get_routing_key_service() -> RoutingKeyService:
    routing_key_repo = RoutingKeyRepository()

    routing_key_service = RoutingKeyService(routing_key_repo=routing_key_repo)
    return routing_key_service


def get_routing_key_subscription_service() -> RoutingKeySubscriptionService:
    routing_key_subscription_repo = RoutingKeySubscriptionRepository()

    routing_key_subscription_service = RoutingKeySubscriptionService(
        routing_key_subscription_repo=routing_key_subscription_repo)
    return routing_key_subscription_service


def get_notificator_service() -> Notificator:
    notificator = Notificator(ws_manager=WSManager)
    return notificator
