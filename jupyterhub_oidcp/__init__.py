import json
import sys
from typing import Optional, List


def _service_to_dict(service: dict) -> Optional[dict]:
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


def _services_to_dict(services: List[dict]) -> List[dict]:
    """
    Convert a list of services to a list of dictionaries.
    """
    r = [_service_to_dict(service) for service in services]
    return [x for x in r if x is not None]


def configure_jupyterhub_oidcp(
    c,
    issuer: Optional[str] = None,
    base_url: Optional[str] = None,
    internal_base_url: Optional[str] = None,
    port: int = 8888,
    services=[],
    vault_path: Optional[str] = None,
    email_pattern: Optional[str] = None,
    admin_email_pattern: Optional[str] = None,
    user_email_pattern: Optional[str] = None,
    oauth_client_allowed_scopes=["inherit"],
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
        "--port", str(port),
    ]
    if issuer:
        service_command.extend([
            "--issuer", issuer,
        ])
    if base_url:
        service_command.extend([
            "--base-url", base_url,
        ])
    if internal_base_url:
        service_command.extend([
            "--internal-base-url", internal_base_url,
        ])
    if vault_path:
        service_command.extend([
            "--vault-path", vault_path,
        ])
    if email_pattern:
        service_command.extend([
            "--email-pattern", email_pattern,
        ])
    if admin_email_pattern:
        service_command.extend([
            "--admin-email-pattern", admin_email_pattern,
        ])
    if user_email_pattern:
        service_command.extend([
            "--user-email-pattern", user_email_pattern,
        ])

    if debug:
        service_command.extend([
            "--debug"
        ])

    service = {
        "name": service_name,
        "admin": False,
        "url": f"http://localhost:{port}/services/{service_name}",
        "display": False,
        "command": service_command,
        "oauth_no_confirm": True,
    }
    if oauth_client_allowed_scopes is not None:
        service["oauth_client_allowed_scopes"] = oauth_client_allowed_scopes
    c.JupyterHub.services.append(service)
