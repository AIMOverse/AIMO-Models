import datetime


class InvitationCode:
    def __init__(self, code: str, expiration_time: datetime.datetime, used: bool):
        self.code = code
        self.expiration_time = expiration_time  # Expiration time of the code
        self.used = used  # If the code is used

    @classmethod
    def from_timestamp(cls, code: str, expiration_timestamp: float, used: bool):
        return cls(code, datetime.datetime.fromtimestamp(expiration_timestamp), used)

    def to_dict(self):
        return {
            "code": self.code,
            "expiration_time": self.expiration_time.timestamp(),  # turn back to timestamp
            "used": self.used,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            code=data["code"],
            expiration_time=datetime.datetime.fromtimestamp(data["expiration_time"]),
            used=data["used"]
        )

    @property
    def is_active(self):
        return not self.used and self.expiration_time > datetime.datetime.now()
