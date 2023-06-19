from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class Device(BaseModel):
    devId: str
    type: str = 'device'
    createdBy: str = 'admin'
    createdDate: datetime = datetime.utcnow()
    devDesc: Optional[str]
    devMaker: Optional[str]
    devSerial: Optional[str]
    devModel: Optional[str]
    devHwVer: Optional[str]
    devFwVer: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "devId": "str",
                "type": "str",
                "devDesc": "str",
                "devMaker": "str",
                "devSerial": "str",
                "devModel": "str",
                "devHwVer": "str",
                "devFwVer": "str",
                "createdBy": "str",
                "createdDate": "str"
            }
        }

    class Settings:
        name = "devices"


class NewDevice(Device):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "devId": "str",
                "password": "str",
                "type": "str",
                "createdDate": "Datetime",
                "devDesc": "str",
                "devMaker": "str",
                "devSerial": "str",
                "devModel": "str",
                "devHwVer": "str",
                "devFwVer": "str",
                "createdBy": "str"
            }
        }
        fields = {'password': {'exclude': True}}


class FirmwareInfo(BaseModel):
    fw_url: str

    class Config:
        schema_extra = {
            "example": {
                "fw_url": "str",
            }
        }
