from .base import BaseOIDHandler

class ProviderInfoHandler(BaseOIDHandler):
    def get(self):
        provider_info = self.provider.providerinfo_endpoint()
        self.log.debug(f"ProviderInfoHandler.get: {provider_info}")
        self.finish_response(provider_info)
