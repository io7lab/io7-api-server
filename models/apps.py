from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class IOTApp(BaseModel):
    appId: str
    createdBy: str = 'admin'
    createdDate: datetime = datetime.utcnow()
    appDesc: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "appId": "str",
                "appDesc": "str",
                "createdBy": "str",
                "createdDate": "str"
            }
        }

    class Settings:
        name = "apps"


class NewIOTApp(IOTApp):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "appId": "str",
                "password": "str",
                "appDesc": "str",
                "createdBy": "str",
                "createdDate": "str"
            }
        }
        fields = {'password': {'exclude': True}}

