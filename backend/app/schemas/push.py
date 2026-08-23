from pydantic import BaseModel, Field


class PushKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionPayload(BaseModel):
    endpoint: str
    keys: PushKeys
    timezone: str = Field(default="UTC", max_length=64)


class PushStatusResponse(BaseModel):
    enabled: bool
    subscribed: bool


class VapidPublicKeyResponse(BaseModel):
    public_key: str


class DispatchRemindersResponse(BaseModel):
    checked: int
    sent: int
    skipped: int
    failed: int
