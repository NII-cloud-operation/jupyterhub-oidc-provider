import json

from .base import BaseOIDHandler


class JwksHandler(BaseOIDHandler):
    def get(self):
        keybundle = self.provider.keybundle
        resp = json.loads(str(keybundle))
        for key in resp['keys']:
            # Remove the private exponent from the key
            for prop in ['d', 'p', 'q', 'dp', 'dq', 'qi', 'k']:
                if prop not in key:
                    continue
                del key[prop]
        self.log.debug(f"JwksHandler.get: {resp}")
        self.set_status(200)
        self.finish(resp)
