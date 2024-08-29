from typing import Optional


class EmailPattern:
    """
    A class to represent an email pattern.
    """

    def __init__(
        self,
        pattern: Optional[str] = None,
        pattern_admin: Optional[str] = None,
        pattern_user: Optional[str] = None,
    ):
        """
        Initialize the email pattern.

        :param pattern: The email pattern.
        :param pattern_admin: The email pattern for an admin user.
        :param pattern_user: The email pattern for a non-admin user.
        """
        self._pattern = pattern
        self._pattern_admin = pattern_admin
        self._pattern_user = pattern_user
        if self._pattern:
            if self._pattern_admin or self._pattern_user:
                raise ValueError(
                    "pattern cannot be set with pattern_admin or pattern_user."
                )
            return
        if not self._pattern_admin or not self._pattern_user:
            raise ValueError("pattern_admin and pattern_user must be set.")

    def get_pattern_for(self, admin: bool) -> Optional[str]:
        """
        Get the email pattern for a user.

        :param admin: Whether the user is an admin.
        :return: The email pattern.
        """
        if self._pattern:
            return self._pattern
        if admin:
            return self._pattern_admin
        return self._pattern_user
