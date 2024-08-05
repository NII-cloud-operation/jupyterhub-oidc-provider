import asyncio
import json
import logging
import os
from urllib.parse import urlparse, urljoin

from tornado import web
from jupyterhub.traitlets import URLPrefix
from jupyterhub.services.auth import HubOAuthCallbackHandler
from traitlets import Unicode, Int, default
from traitlets.config.application import Application, catch_config_error
from .handlers import (
    ProviderInfoHandler,
    AuthorizationHandler,
    TokenHandler,
    JwksHandler,
    UserInfoHandler,
)
from .provider import HubOAuthProvider


logger = logging.getLogger(__name__)


class OpenIDConnectProviderApp(Application):
    """
    A jupyter Application that provides OpenID Connect endpoints.
    """

    base_url = Unicode(
        help="The base URL of the application."
    ).tag(config=True)

    service_prefix = Unicode(
        help="The service prefix of the application."
    ).tag(config=True)

    port = Int(8888, help="The port to listen on.").tag(config=True)

    services = Unicode(
        "[]",
        help="The services to provide OpenID Connect for."
    ).tag(config=True)

    vault_path = Unicode(
        help="The path to the vault.",
    ).tag(config=True)

    email_pattern = Unicode(
        help="""The format of the email address to use for the user.
        The email address will be formatted using this pattern. For example,
        if the pattern is '{uid}@example.com' and the user id is 'user1',
        the email address will be 'user1@example.com'""",
    ).tag(config=True)

    aliases = {
        "base-url": "OpenIDConnectProviderApp.base_url",
        "port": "OpenIDConnectProviderApp.port",
        "services": "OpenIDConnectProviderApp.services",
        "vault-path": "OpenIDConnectProviderApp.vault_path",
    }

    hub_prefix = URLPrefix('/hub/')

    @default("base_url")
    def _base_url_default(self):
        base_url = os.environ['JUPYTERHUB_BASE_URL']
        return base_url
    
    @default("service_prefix")
    def _service_prefix_default(self):
        service_prefix = os.environ['JUPYTERHUB_SERVICE_PREFIX']
        return service_prefix

    @catch_config_error
    def initialize(self, argv=None):
        """
        Initialize the application.
        """
        super().initialize(argv)
        self.log.info("Initializing OpenID Connect Provider App")

    def start(self):
        """
        Start the application.
        """
        self._configure_python_logging()
        self.log.info("Starting OpenID Connect Provider App")
        asyncio.run(self._start())

    async def _start(self):
        """
        Start the application. This is an async method.
        """
        app = self._make_app()
        app.listen(self.port)
        self.log.info(f"Listening on port {self.port}")
        await asyncio.Event().wait()

    def _configure_python_logging(self):
        self.log.info(f"Configuring logging level: {self.log_level}")
        # (0, 10, 20, 30, 40, 50, "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL")
        level = logging.INFO
        if self.log_level == 0:
            level = logging.WARNING
        elif self.log_level == 10 or self.log_level == "DEBUG":
            level = logging.DEBUG
        elif self.log_level == 20 or self.log_level == "INFO":
            level = logging.INFO
        elif self.log_level == 30 or self.log_level == "WARN":
            level = logging.WARN
        elif self.log_level == 40 or self.log_level == "ERROR":
            level = logging.ERROR
        elif self.log_level == 50 or self.log_level == "CRITICAL":
            level = logging.CRITICAL
        logging.basicConfig(level=level)
        logger.info(f"Logging level set to {level}")

    def _make_app(self):
        self.log.info(f"Making OpenID Connect Provider App base_url={self.base_url}, service_prefix={self.service_prefix}")
        services = json.loads(self.services)
        self.log.info(f"Services: {services}")
        provider = HubOAuthProvider(
            "jupyterhub",
            services,
            urljoin(self.base_url, self.service_prefix),
            vault_path=self.vault_path,
            email_pattern=self.email_pattern,
        )
        oauth_callback_url = os.environ.get(
            'JUPYTERHUB_OAUTH_CALLBACK_URL',
            urljoin(self.service_prefix, 'oauth_callback'))
        tornado_settings = dict(
            app=self,
            log=self.log,
            base_url=self.base_url,
            service_prefix=self.service_prefix,
            hub_prefix=self.hub_prefix,
            cookie_secret=os.urandom(32),
        )
        handler_settings = dict(
            provider=provider,
        )
        service_prefix = self.service_prefix
        if service_prefix.endswith('/'):
            service_prefix = service_prefix[:-1]
        return web.Application([
            (oauth_callback_url, HubOAuthCallbackHandler),
            (f'{service_prefix}/.well-known/openid-configuration', ProviderInfoHandler, handler_settings),
            (f'{service_prefix}/authorization', AuthorizationHandler, handler_settings),
            (f'{service_prefix}/token', TokenHandler, handler_settings),
            (f'{service_prefix}/userinfo', UserInfoHandler, handler_settings),
            (f'{service_prefix}/jwks.json', JwksHandler, handler_settings),
        ], **tornado_settings)

if __name__ == "__main__":
    OpenIDConnectProviderApp.launch_instance()
