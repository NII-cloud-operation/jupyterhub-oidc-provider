from .base import BaseOIDHandler

class UserInfoHandler(BaseOIDHandler):
    def get(self):
        resp = self.provider.userinfo_endpoint(
            request=self.request.uri,
            authn=self.request.headers.get('Authorization', None)
        )
        self.log.debug(f"UserInfoHandler.post: {resp.message}")
        self.finish_response(resp)
