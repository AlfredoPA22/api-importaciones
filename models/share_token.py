from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ShareToken(BaseModel):
    import_id: str
    expires_at: Optional[datetime] = None
    is_active: bool = True

class ShareTokenResponse(BaseModel):
    token: str
    share_url: str
    expires_at: Optional[datetime] = None
    is_active: bool

