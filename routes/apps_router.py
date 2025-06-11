from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timezone, timedelta

from models import IOTApp, NewIOTApp, MemberDevice, Device
from secutils import authenticate
from environments import Database, dynsec_get_client_role, dynsec_get_appId
from dynsec.apps_dynsec import add_dynsec_app, delete_dynsec_app, add_dynsec_member, remove_dynsec_member, update_dynsec_members
from dynsec.roles_dynsec import delete_dynsec_role

apps_db = Database(IOTApp.Settings.name)
device_db = Database(Device.Settings.name)
router = APIRouter(tags=['Apps'])
kst=timezone(timedelta(hours=9))

@router.get('/', response_model=List[IOTApp])
async def get_apps(jwt: str = Depends(authenticate)) -> dict:
    """
    Retrieve a list of all registered IOT application IDs.
    
    This endpoint returns all application IDs registered in the system.
    The type of an application ID is IOTApp in io7 platform.
    Authentication is required to access this endpoint.
    
    Returns:
    - A list of IOTApp objects containing application details
    """
    return apps_db.getAll()

@router.post('/')
async def add_app(newApp: NewIOTApp, jwt: str = Depends(authenticate)) -> IOTApp:
    """
    Register a new IOT application ID in the system.
    
    This endpoint allows creation of a new application ID with the provided details.
    Authentication is required to access this endpoint.
    
    Caution:
    - Application IDs cannot start with '$' or be named 'admin'
    - Application ID must be unique across both apps and devices
    - The password provided will be used for MQTT authentication
    
    Returns:
    - The newly created IOTApp object
    """
    if newApp.appId.startswith('$') or newApp.appId == 'admin':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The Id({newApp.appId}) can not be registered for AppId."
        )
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
async def get_application(appId: str, jwt: str = Depends(authenticate)) -> IOTApp:
    """
    Retrieve details for a specific IOT application ID.
    
    This endpoint returns the application details for the specified appId.
    Authentication is required to access this endpoint.
    
    Parameters:
    - appId: The unique identifier of the application to retrieve
    
    Returns:
    - An IOTApp object containing the application details
    """
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppID(appId:{appId}) does not exist"
        )
    return app

@router.delete('/{appId}')
async def del_appId(appId: str, jwt: str = Depends(authenticate)) -> dict:
    """
    Delete an IOT application from the system.
    
    This endpoint removes the application ID with the specified appId from the database
    and also deletes the corresponding MQTT ACL and roles.
    Authentication is required to access this endpoint.
    
    Caution:
    - This operation cannot be undone
    - All device associations and access permissions will be permanently removed
    
    Parameters:
    - appId: The unique identifier of the application to delete
    
    Returns:
    - A confirmation message with the deleted application ID
    """
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppId(appId:{appId}) does not exist"
        )
    
    if app.get('restricted', None):
        delete_dynsec_role(f'$apps_{appId}')
    delete_dynsec_app(appId)
    apps_db.delete(apps_db.qry.appId == appId)
    return {"message": "AppId deleted successfully", "appId": appId}

@router.put('/{appId}/addMembers')
async def addMembers(appId: str, members: List[MemberDevice], jwt: str = Depends(authenticate)) -> dict:
    """
    Add multiple devices to the `appId`'s role, so the appId can access the devices' events and commands.

    When adding, the access to the evt & the cmd can be configured as needed. 
    For example, {evt : true} will allow access to the event from the device, and {evt : false} will deny.
    Likewise the command to the device can be configured. eg. {cmd : true}
    
    Caution:
    - Ensure proper access control to avoid security issues
    - Setting both evt and cmd to false effectively removes access
    - Only restricted applications can have members
    - The member is not updated if it already exists, so if the access to the existing member needs to be changed, then use updateMembers API.
    
    Parameters:
    - appId: Application ID to grant access to
    - members: List of Device information including access permissions
    ```
    [
        {
            "devId": "lamp1",
            "evt": "true",
            "cmd": "true"
        },
        {
            "devId": "lamp2",
            "evt": "true",
            "cmd": "true"
        }
    ]
    ```
    
    Returns:
    - Confirmation message with application and device IDs
    """
    if dynsec_get_appId(appId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppId({appId}) does not exist"
        )
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if app and app.get('restricted', None) in [False, None]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The AppId({appId}) doesn't have members."
        )

    add_dynsec_member(appId, members)
    return {"message": "Device is added successfully", "appId": appId, "members" : members}

@router.put('/{appId}/removeMembers')
async def removeMembers(appId: str, members: list, jwt: str = Depends(authenticate)) -> dict:
    """
    Remove multiple devices from the `appId`'s role, so the `appId` can't access them.
    
    This endpoint revokes the application's access to the specified devices.
    Authentication is required to access this endpoint.
    
    Caution:
    - This operation cannot be undone
    - Any services depending on this access will stop working immediately
    - The devices will no longer be accessible by this application
    
    Parameters:
    - appId: Application ID to revoke access from
    - members: List of device IDs to remove from application's access control
    ```
    [
        "lamp1", "lamp2"
    ]
    ```
    
    Returns:
    - Confirmation message with application and device IDs
    """
    if dynsec_get_appId(appId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppId({appId}) does not exist"
        )
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if app and app.get('restricted', None) in [False, None]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The AppId({appId}) doesn't have members."
        )

    remove_dynsec_member(appId, members)
    return {"message": "Device is removed successfully", "appId": appId, "members": members}

@router.get('/{appId}/members')
async def get_app_members(appId: str, detail: bool = False, jwt: str = Depends(authenticate)) -> dict:
    """
    Retrieve the list of devices that are members of a specific application.
    
    This endpoint returns the devices that the application has access to,
    along with their access permissions (event and command access).
    Authentication is required to access this endpoint.
    
    Caution:
    - Only restricted applications can have members
    - Application must exist in both the database and dynamic security system
    
    Parameters:
    - appId: The unique identifier of the application to get members for
    - detai: Optional parameter to get the detail ACLs as below
    ```
        http://api-server:2009/app-ids/<appId>/members?detail=True
    ```
    
    Returns:
    - A dictionary containing the device with the respective access to topics(evt/cmd). 
    - If detail=True is passed, the result has the role information for the application including
      all device access control lists with their permissions
    """
    if dynsec_get_appId(appId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppId(appId:{appId}) does not exist"
        )
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if app and app.get('restricted', None) in [False, None]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The AppId({appId}) doesn't have members."
        )

    return dynsec_get_client_role(appId, detail=detail)

@router.put('/{appId}/updateMembers')
async def updateMembers(appId: str, members: List[MemberDevice], jwt: str = Depends(authenticate)) -> dict:
    """
    Update all member devices for an application with a single operation.
    
    This endpoint replaces the existing device memberships with the provided list.
    
    Caution:
    - This is a complete replacement operation
    - Any device not included in the new list will lose access
    - Authentication is required to access this endpoint
    
    Parameters:
    - appId: Application ID to update memberships for
    - members: Complete list of desired device memberships with access permissions
    ```
    [
        {
            "devId": "lamp1",
            "evt": "true",
            "cmd": "true"
        },
        {
            "devId": "lamp2",
            "evt": "true",
            "cmd": "false"
        }
    ]
    ```
    
    Returns:
    - Confirmation message with the updated application ID
    """
    if dynsec_get_appId(appId) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AppId(appId:{appId}) does not exist"
        )
    app = apps_db.getOne(apps_db.qry.appId == appId)
    if app and app.get('restricted', None) in [False, None]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The AppId({appId}) doesn't have members."
        )

    update_dynsec_members(appId, members)
    return {"message": "Members are updated successfully", "appId": appId}