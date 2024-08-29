import json

from .base import BaseOIDHandler


class JwksHandler(BaseOIDHandler):
    def get(self):
        keybundle = self.provider.keybundle
        resp = json.loads(str(keybundle))
        for key in resp['keys']:
            # Remove the private exponent from the key
            del key['d']
            if 'k' in key:
                del key['k']
        self.log.debug(f"JwksHandler.get: {resp}")
        self.set_status(200)
        self.finish(resp)
