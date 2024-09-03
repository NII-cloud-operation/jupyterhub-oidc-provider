from abc import ABC, abstractmethod


class UserInfo:
    @classmethod
    def from_huboauth_user(cls, response: dict):
        if 'kind' not in response or response['kind'] != 'user':
            raise ValueError(
                f"Invalid response kind: {response.get('kind', None)}"
            )
        if 'name' not in response:
            raise ValueError("Missing 'name' in response.")
        return cls(
            uid=response["name"],
            admin=response.get("admin", False)
        )

    def __init__(self, uid: str, admin: bool):
        self.uid = uid
        self.admin = admin


class NoUserError(Exception):
    pass


class UserStore(ABC):
    @abstractmethod
    def set_user(self, user: UserInfo):
        raise NotImplementedError

    @abstractmethod
    def get_user(self, uid: str) -> UserInfo:
        raise NotImplementedError
