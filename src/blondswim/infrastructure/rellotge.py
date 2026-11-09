"""Rellotge del sistema (port `Rellotge`)."""

from datetime import datetime


class RellotgeSistema:
    def ara(self) -> datetime:
        return datetime.now()
