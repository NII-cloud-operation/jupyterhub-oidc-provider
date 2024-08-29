from .base import UserStore, UserInfo, NoUserError

import logging


logger = logging.getLogger(__name__)


class MemoryUserStore(UserStore):
    def __init__(self):
        self.users = {}

    def set_user(self, user: UserInfo):
        logger.debug(f"MemoryUserStore.set_user: {user}")
        self.users[user.uid] = user

    def get_user(self, uid: str) -> UserInfo:
        if uid not in self.users:
            raise NoUserError(f"User {uid} not found.")
        return self.users[uid]
