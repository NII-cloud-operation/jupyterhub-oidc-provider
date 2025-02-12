import json
import unittest
from unittest.mock import MagicMock, patch

from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase

from jupyterhub_oidcp.handlers.jwks import JwksHandler


class TestJwksHandler(AsyncHTTPTestCase):
    def get_app(self):
        # Mock provider and keybundle
        self.mock_provider = MagicMock()
        self.mock_keybundle = MagicMock()

        # Sample JWKS data including private key parameters
        self.mock_keybundle.__str__.return_value = json.dumps({
            "keys": [
                {
                    "kty": "RSA",
                    "kid": "test-key",
                    "n": "base64modulus",
                    "e": "AQAB",
                    "d": "private-d",
                    "p": "private-p",
                    "q": "private-q",
                    "dp": "private-dp",
                    "dq": "private-dq",
                    "qi": "private-qi",
                    "k": "private-k"
                }
            ]
        })
        self.mock_provider.keybundle = self.mock_keybundle

        return Application([(
            r"/jwks",
            JwksHandler,
            dict(
                provider=self.mock_provider,
                userstore=MagicMock(),
            ),
        )])

    def test_get_jwks(self):
        response = self.fetch("/jwks", method="GET")
        self.assertEqual(response.code, 200)

        jwks_data = json.loads(response.body)
        self.assertIn("keys", jwks_data)
        self.assertEqual(len(jwks_data["keys"]), 1)

        key = jwks_data["keys"][0]
        self.assertNotIn("d", key)
        self.assertNotIn("p", key)
        self.assertNotIn("q", key)
        self.assertNotIn("dp", key)
        self.assertNotIn("dq", key)
        self.assertNotIn("qi", key)
        self.assertNotIn("k", key)

        self.assertEqual(key["kty"], "RSA")
        self.assertEqual(key["kid"], "test-key")
        self.assertEqual(key["n"], "base64modulus")
        self.assertEqual(key["e"], "AQAB")
