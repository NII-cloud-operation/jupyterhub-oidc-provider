import json
import sys
from urllib.parse import urljoin


def _service_to_dict(service: dict) -> dict | None:
    """
    Convert a service to a dictionary.
    """
    if 'oauth_client_id' not in service:
        raise ValueError("Service must have an 'oauth_client_id' key.")
    if 'api_token' not in service:
        raise ValueError("Service must have an 'api_token' key.")
    if 'redirect_uris' not in service:
        raise ValueError("Service must have an 'redirect_uris' key.")
    return {
        "oauth_client_id": service['oauth_client_id'],
        "api_token": service['api_token'],
        "redirect_uris": service['redirect_uris'],
    }

def _services_to_dict(services: list[dict]) -> list[dict]:
    """
    Convert a list of services to a list of dictionaries.
    """
    r = [_service_to_dict(service) for service in services]
    return [x for x in r if x is not None]


def configure_jupyterhub_oidcp(
    c,
    base_url: str | None=None,
    services=[],
    vault_path: str | None=None,
    debug=False
):
    """
    Add the OIDC service to the JupyterHub configuration.
    """
    service_name = "oidcp"
    services_def = json.dumps(_services_to_dict(services))

    service_command = [
        sys.executable,
        "-m", "jupyterhub_oidcp.main",
        "--services", services_def,
    ]
    if base_url:
        service_command.extend([
            "--base-url", base_url,
        ])
    if vault_path:
        service_command.extend([
            "--vault-path", vault_path,
        ])

    if debug:
        service_command.extend([
            "--debug"
        ])

    c.JupyterHub.services.append({
        "name": service_name,
        "admin": False,
        "url": f"http://localhost:8888/services/{service_name}",
        "display": False,
        "command": service_command,
        "oauth_no_confirm": True,
        "oauth_client_allowed_scopes": ["inherit"]
    })
