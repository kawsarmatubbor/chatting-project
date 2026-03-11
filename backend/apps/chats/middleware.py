from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token")

        if token:
            try:
                access_token = AccessToken(token[0])
                user = await sync_to_async(User.objects.get)(id=access_token["user_id"])
                scope["user"] = user
            except Exception:
                scope["user"] = None
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)