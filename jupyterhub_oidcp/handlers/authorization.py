from jupyterhub.services.auth import HubOAuthenticated
from tornado import web

from .base import BaseOIDHandler
from ..provider import HubOAuthAuthnMethod
from ..userstore import UserInfo


class AuthorizationHandler(HubOAuthenticated, BaseOIDHandler):
    @web.authenticated
    def get(self):
        resp = self.provider.authorization_endpoint(
            request=self.request.uri,
            cookie=HubOAuthAuthnMethod.current_user_to_cookie(
                self.get_current_user()
            )
        )
        user = self.get_current_user()
        self.log.debug(f"AuthorizationHandler.get: {resp}, user={user}")
        userinfo = UserInfo.from_huboauth_user(user)
        self.userstore.set_user(userinfo)
        self.finish_response(resp)
