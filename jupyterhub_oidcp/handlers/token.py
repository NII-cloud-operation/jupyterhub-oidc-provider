from .base import BaseOIDHandler

class TokenHandler(BaseOIDHandler):
    def post(self):
        resp = self.provider.token_endpoint(
            request=self.request.body.decode('utf-8'),
            authn=self.request.headers.get('Authorization', None)
        )
        self.log.debug(f"TokenHandler.post: {resp.message}")
        self.finish_response(resp)
