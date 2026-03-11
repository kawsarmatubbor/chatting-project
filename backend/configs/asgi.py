import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.chats.routing import websocket_urlpatterns
from apps.chats.middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})