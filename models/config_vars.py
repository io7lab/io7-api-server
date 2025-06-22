from pydantic import BaseModel

class ConfigVar(BaseModel):
    key: str
    value: str

    class Config:
        schema_extra = {
            "example": {
                "key": "str",
                "value": "str"
            }
        }

    class Settings:
        name = "config_var"