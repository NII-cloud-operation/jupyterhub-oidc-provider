import json
from urllib.parse import urlparse

from .base import BaseOIDHandler

class ProviderInfoHandler(BaseOIDHandler):
    def get(self):
        provider_info = self.provider.providerinfo_endpoint()
        self.log.debug(f"ProviderInfoHandler.get: {provider_info}")
        self.finish_response(provider_info)


class InternalProviderInfoHandler(BaseOIDHandler):
    def get(self):
        if not self.internal_base_url:
            self.set_status(404)
            self.finish({"error": "Internal base URL not set"})
            return
        provider_info = self.provider.providerinfo_endpoint()
        self.log.debug(f"InternalProviderInfoHandler.get: {provider_info}")
        if provider_info.status_code != 200:
            self.finish_response(provider_info)
            return
        response = json.loads(provider_info.message)
        for uri in ["token_endpoint", "jwks_uri", "userinfo_endpoint"]:
            response[uri] = self._fix_uri(response[uri])
        self.set_status(200)
        self.finish(response)

    @property
    def internal_base_url(self):
        return self.settings.get("internal_base_url", None)

    def _fix_uri(self, uri):
        internal = urlparse(self.internal_base_url)
        parsed = urlparse(uri)
        return parsed._replace(
            scheme=internal.scheme,
            netloc=internal.netloc,
        ).geturl()
