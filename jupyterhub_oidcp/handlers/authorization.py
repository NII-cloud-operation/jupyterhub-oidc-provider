from jupyterhub.services.auth import HubOAuthenticated
from tornado import web

from .base import BaseOIDHandler
from ..provider import HubOAuthAuthnMethod

class AuthorizationHandler(HubOAuthenticated, BaseOIDHandler):
    @web.authenticated
    def get(self):
        resp = self.provider.authorization_endpoint(
            request=self.request.uri,
            cookie=HubOAuthAuthnMethod.current_user_to_cookie(self.get_current_user())
        )
        user = self.get_current_user()
        self.log.debug(f"AuthorizationHandler.get: {resp}, user={user}")
        self.finish_response(resp)
