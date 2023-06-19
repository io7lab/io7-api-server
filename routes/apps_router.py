from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timezone, timedelta

from models import IOTApp, NewIOTApp, Device
from secutils import authenticate
from environments import Database
from dynsec.apps_dynsec import add_dynsec_app, delete_dynsec_app

apps_db = Database(IOTApp.Settings.name)
device_db = Database(Device.Settings.name)
router = APIRouter(tags=['Apps'])
kst=timezone(timedelta(hours=9))

@router.get('/', response_model=List[IOTApp])
async def get_apps(jwt: str = Depends(authenticate)) -> dict:
    return apps_db.getAll()

@router.post('/')
async def add_app(newApp: NewIOTApp, jwt: str = Depends(authenticate)) -> IOTApp:
    qryApp = apps_db.getOne(apps_db.qry.appId == newApp.appId)
    qryDevice = device_db.getOne(device_db.qry.devId == newApp.appId)
    if qryApp or qryDevice:
        if qryApp:
            detail = f"The Id({newApp.appId}) is already registered for AppId."
        else:
            detail = f"The Id({newApp.appId}) is already registered for Device."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
    newApp.createdDate = newApp.createdDate.replace(tzinfo=timezone.utc).astimezone(tz=kst)
    newApp.createdDate = str(newApp.createdDate.strftime('%Y-%m-%d %H:%M:%S'))
    add_dynsec_app(newApp)
    apps_db.insert(newApp)
    return newApp.dict()

@router.get('/{appId}', response_model=IOTApp)
async def get_appId(appId: str, jwt: str = Depends(authenticate)) -> IOTApp:
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppID(appId:{appId}) does not exist"
        )
    return app

@router.delete('/{appId}')
async def del_appId(appId: str, jwt: str = Depends(authenticate)) -> dict:
    doc_ids = apps_db.delete(apps_db.qry.appId == appId)
    if not doc_ids or len(doc_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppId(appId:{appId}) does not exist"
        )
    delete_dynsec_app(appId)
    return {"message": "AppId deleted successfully", "appId": appId}
