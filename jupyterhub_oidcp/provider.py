import logging
import json
import tempfile
import time
from typing import List, Optional
from urllib.parse import urljoin

from oic import rndstr
from oic.oic.provider import Provider
from oic.utils.authn.authn_context import AuthnBroker
from oic.utils.authn.user import UserAuthnMethod
from oic.utils.clientdb import BaseClientDatabase
from oic.utils.sdb import create_session_db
from oic.utils.keyio import key_setup


logger = logging.getLogger(__name__)
COOKIE_PREFIX = "jupyterhub:"


class ServicesClientDatabase(BaseClientDatabase):
    """
    A subclass of oic.utils.clientdb.BaseClientDatabase
    that wraps the JupyterHub services
    """

    services: List[dict]

    def __init__(self, services: List[dict]):
        """
        Initialize the client database.
        """
        self.services = self._validate(services)

    def _validate(self, services: List[dict]) -> List[dict]:
        """
        Validate the services.
        """
        if services is None:
            raise ValueError("Services must not be None.")
        if not isinstance(services, list):
            raise ValueError("Services must be a list.")
        validated = []
        for base_service in services:
            validated_service = {}
            validated_service.update(base_service)
            validated.append(validated_service)
            if 'redirect_uris' in validated_service:
                validated_service['redirect_uris'] = [
                    (uri if isinstance(uri, tuple) else (uri, None))
                    for uri in validated_service['redirect_uris']
                ]
            service = validated_service
            if 'oauth_client_id' not in service:
                raise ValueError("Service must have an 'oauth_client_id' key.")
            if 'api_token' not in service:
                raise ValueError("Service must have an 'api_token' key.")
            if 'redirect_uris' not in service:
                raise ValueError("Service must have an 'redirect_uris' key.")
            for uri in service['redirect_uris']:
                if not isinstance(uri, tuple):
                    raise ValueError("Redirect URI must be a tuple.")
                if len(uri) != 2:
                    raise ValueError("Redirect URI must have two elements.")
                first, second = uri
                if not isinstance(first, str):
                    raise ValueError(
                        "Redirect URI first element must be a string."
                    )
                if second is not None and not isinstance(second, str):
                    raise ValueError(
                        "Redirect URI second element must be a string or None."
                    )
            validated_service['client_id'] = base_service.get(
                'oauth_client_id'
            )
            validated_service['client_secret'] = base_service.get('api_token')
            validated_service['client_salt'] = rndstr(8)
        logger.info("Validated services")
        return validated

    def __getitem__(self, key):
        """
        Get an item from the client database.
        """
        logger.info(f"Getting item from client database: {key}")
        for service in self.services:
            if service['oauth_client_id'] == key:
                logger.info(f"Found item in client database: {key}")
                return service
        raise KeyError(key)

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def keys(self):
        """
        Get the keys of the client database.
        """
        logger.info("Getting keys from client database")
        return [service['oauth_client_id'] for service in self.services]

    def items(self):
        """
        Get the items of the client database.
        """
        logger.info("Getting items from client database")
        return [
            (service['oauth_client_id'], service)
            for service in self.services
        ]


class HubOAuthAuthnMethod(UserAuthnMethod):
    """
    A subclass of oic.utils.authn.user.UserAuthnMethod
    that wraps the JupyterHub services
    """

    @staticmethod
    def current_user_to_cookie(user):
        """
        Store the current user information in a cookie.
        """
        logger.info(f"Storing current user in cookie: {user}")
        if user is None:
            raise ValueError("User must not be None.")
        if "name" not in user:
            raise ValueError("User must have a 'name' key.")
        if "created" not in user:
            raise ValueError("User must have a 'created' key.")
        return COOKIE_PREFIX + json.dumps({
            "uid": user["name"],
            "created": user["created"],
        })

    @staticmethod
    def cookie_to_current_user(cookie):
        """
        Retrieve the current user information from a cookie.
        """
        logger.info(f"Retrieving current user from cookie: {cookie}")
        if cookie is None:
            raise ValueError("Cookie must not be None.")
        if not cookie.startswith(COOKIE_PREFIX):
            raise ValueError("Cookie must start with the cookie prefix.")
        cookie = cookie[len(COOKIE_PREFIX):]
        return json.loads(cookie)

    def __init__(self):
        """
        Initialize the authentication method.
        """
        UserAuthnMethod.__init__(self, None)

    def authenticated_as(self, cookie=None, authorization=None, **kwargs):
        """
        Authenticate as a user.

        HubOAuthProvider passes the user information
        as the jupyterhub_currentuser.
        """
        logger.info("Authenticating as user: " +
                    f"{cookie}, {authorization}, {kwargs}")
        user = HubOAuthAuthnMethod.cookie_to_current_user(cookie)
        ts = int(time.time())
        return user, ts


def _get_authn_broker():
    authn_broker = AuthnBroker()
    authn = HubOAuthAuthnMethod()
    authn_broker.add("huboauth", authn)
    return authn_broker


def _authz(user, client_id: Optional[str] = None):
    logger.info(f"Authorizing user: {user}, {client_id}")
    return ""


def _client_authn(provider, areq, authn):
    logger.info(f"Client authentication: {provider}, {areq}, {authn}")
    redirect_uri = areq['redirect_uri']
    for client_id, params in provider.cdb.items():
        if redirect_uri not in [uri for uri, _ in params['redirect_uris']]:
            continue
        logger.info(f"Found client for redirect URI: {redirect_uri}")
        return client_id
    raise ValueError(f"Client not found for redirect URI: {redirect_uri}")


def _userinfo_factory(email_pattern: Optional[str] = None):
    def _userinfo(uid, client_uid, userinfo_claims):
        logger.info(f"Getting userinfo: {uid}, " +
                    f"{client_uid}, {userinfo_claims}")
        userinfo = {
            "sub": uid,
            "name": uid,
            "preferred_username": uid,
        }
        if email_pattern:
            userinfo["email"] = email_pattern.format(uid=uid)
        return userinfo
    return _userinfo


class HubOAuthProvider(Provider):
    """
    A subclass of oic.oic.provider.Provider that wraps the JupyterHub services
    """

    def __init__(
        self,
        name,
        services: List[dict],
        baseurl: str,
        vault_path: Optional[str] = None,
        email_pattern: Optional[str] = None,
    ):
        """
        Initialize the provider.
        """
        Provider.__init__(
            self,
            name,
            create_session_db(
                baseurl,
                secret=rndstr(32),
                password=rndstr(32)
            ),
            ServicesClientDatabase(services),
            _get_authn_broker(),
            _userinfo_factory(email_pattern),
            _authz,
            _client_authn,
            baseurl=baseurl
        )
        self._init_keys(vault_path)

    def _init_keys(self, vault_path: Optional[str] = None):
        if vault_path is None or vault_path == "":
            vault_path = tempfile.mkdtemp()
        self.keybundle = key_setup(
            vault_path,
            sig={"format": "jwk", "alg": "rsa"},
        )
        keyjar = self.keyjar
        try:
            keyjar[""].append(self.keybundle)
        except KeyError:
            keyjar[""] = self.keybundle
        logger.info(f"Initialized keys: {vault_path}")
        self.jwks_uri = urljoin(self.baseurl, "jwks.json")
