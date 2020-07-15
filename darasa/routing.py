from channels.routing import ProtocolTypeRouter, URLRouter
import apps.roulette.routing

application = ProtocolTypeRouter(
    {"http": URLRouter(apps.roulette.routing.urlpatterns),}
)
