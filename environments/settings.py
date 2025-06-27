from typing import Optional

from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
import random
import string

def gen_secret_key():
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(20)) 

class Settings(BaseSettings):
    DATABASE_DIR = 'data/db'                   # Database directory
    SECRET_KEY = gen_secret_key()           # JWT Token Gen Secret Key
    SSL_KEY: Optional[str] = None           # SSL Key Path
    SSL_CERT: Optional[str] = None          # SSL Cert Path
    PORT: int = 3001                        # API Server Port
    HOST: str = '0.0.0.0'                   # API Server Host
    TEMPLATES = Jinja2Templates(directory="html/")  # Jinja2 Templates Directory
    DynSecUser: Optional[str] = None        # Mosquitto Dynamic Security User
    DynSecPass: Optional[str] = None        # Mosquitto Dynamic Security Password
    DynSecPath: Optional[str] = None        # Mosquitto Dynamic Security JSON Path
    MQTT_HOST: Optional[str] = "127.0.0.1"  # MQTT Host
    MQTT_PORT: Optional[int] = 1883         # MQTT Port
    MQTT_SSL_CERT: Optional[str] = None     # MQTT SSL Cert Path
    INFLUXDB_PROTOCOL: Optional[str] = "http"   # INFLUXDB Access Protocol
    LOG_LEVEL: Optional[str] = "INFO"       # Log Level

    class Config:
        env_file = "data/.env"
