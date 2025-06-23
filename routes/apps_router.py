from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Body
from datetime import timezone, timedelta, datetime

from models import IOTApp, NewIOTApp, MemberDevice, Device
from secutils import authenticate
from environments import Database, dynsec_get_client_role, dynsec_get_appId, dynsec_all_appIds
from dynsec.apps_dynsec import add_dynsec_app, delete_dynsec_app, add_dynsec_member, remove_dynsec_member, update_dynsec_members
from dynsec.roles_dynsec import delete_dynsec_role

apps_db = Database(IOTApp.Settings.name)
devices_db = Database(Device.Settings.name)
router = APIRouter(tags=['Apps'])

@router.get('/', response_model=List[dict])
async def get_apps(broken:bool = False, jwt: str = Depends(authenticate)) -> dict:
    """
    Retrieve a list of all registered IOT application IDs.
    
    This endpoint returns all application IDs registered in the system.
    The type of an application ID is IOTApp in io7 platform.
    Authentication is required to access this endpoint.

    Cautions:
    - AppId authentication & authorization is managed by the MQTT Dynamic Security Plugin
    - AppId metadata is stored in the TinyDB database
    - Inconsistencies between these two data sources can result in broken device states
    - Use `?broken=true` to retrieve only AppId with database/MQTT configuration mismatches
    
    Returns:
    - A list of IOTApp objects containing application details
    """
    if broken:
        dynsec_apps = dynsec_all_appIds()
        db_apps = apps_db.getAll()
        mal_dynsec_apps = []
        mal_db_apps = []
        for dyn_app in dynsec_apps:
            a = apps_db.getOne(apps_db.qry.appId == dyn_app)
            if a is None:
                db_a = IOTApp(appId = dyn_app).dict()
                db_a['toFix'] = 'tinydb'
                mal_dynsec_apps.append(db_a)
        for db_app in db_apps:
            a = dynsec_get_appId(db_app['appId'])
            if a is None:
                db_a = dict(db_app)
                db_a['toFix'] = 'dynsec'
                mal_db_apps.append(db_a)
        return(mal_db_apps + mal_dynsec_apps)
    else:
        app_list = []
        db_apps = apps_db.getAll()
        for db_app in db_apps:
            a = dynsec_get_appId(db_app['appId'])
            db_a = dict(db_app)
            if a is None:
                db_a['toFix'] = 'dynsec'
            app_list.append(db_a)
        return app_list

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
    qryDevice = devices_db.getOne(devices_db.qry.devId == newApp.appId)
    if qryApp or qryDevice:
        if qryApp:
            detail = f"The Id({newApp.appId}) is already registered for AppId."
        else:
            detail = f"The Id({newApp.appId}) is already registered for Device."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

    newApp.createdDate = newApp.createdDate.replace(tzinfo=timezone.utc)
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
            detail=f"AppID({appId}) does not exist"
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
            detail=f"AppId({appId}) does not exist"
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


@router.patch('/{appId}/update')
async def update_apps(
    appId: str, updateData: dict = Body(
        {
            "password": "str",
            "restricted": "false",
            "appDesc": "str"
        }
    ),
    jwt: str = Depends(authenticate)) -> IOTApp:
    """
    Update application information and fix broken application states.
    
    This endpoint allows updating application metadata and fixing inconsistencies between the database
    and MQTT dynamic security configurations. It handles various scenarios including complete updates,
    password-only fixes for missing MQTT configurations, and database-only repairs.
    Authentication is required to access this endpoint.
    
    Caution:
    - Application IDs cannot start with '$' or be named 'admin'
    - Password is only allowed when recreating missing MQTT dynamic security configurations
    - Missing MQTT configurations will be recreated if password is provided
    - The restricted field controls whether the application can have member devices
    
    Parameters:
    - appId: The unique identifier of the application to update
    - updateData: Dictionary containing the fields to update (password, restricted, appDesc, etc.)
    
    Returns:
    - The updated IOTApp object with current information
    """
    if appId.startswith('$') or appId == 'admin':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The Id({appId}) cannot be registered for AppId."
        )

    db_app = apps_db.getOne(apps_db.qry.appId == appId)
    dyn_app = dynsec_get_appId(appId)
    if db_app: 
        if dyn_app:
            # Both db_app & dyn_app found; update the information in TinyDB 
            if 'password' in updateData:
                # Filter out the password change since it's not allowed
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="AppId token cannot be changed"
                )
            else: 
                # Update the information in TinyDB
                for key, value in updateData.items():
                    if key in db_app:  # Only update existing keys
                        db_app[key] = value
                #print(db_app)
                theApp = IOTApp(**db_app)
                theApp.appId=appId
                theApp.createdBy='admin'
                theApp.createdDate = str(theApp.createdDate.strftime('%Y-%m-%d %H:%M:%S'))
                apps_db.insert(theApp)
                return theApp
        elif 'password' in updateData:
            # No dyn_app found; create dyn_app
            db_app['password'] = updateData['password']
            newApp = NewIOTApp(**db_app)
            add_dynsec_app(newApp)
            return newApp
        else:
            # No dyn_app found but can't create it since no password is given
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No change was made"
            )
    else:
        # dyn_app exists but no db_app found; filling in the metadata information
        updateData['appId'] = appId
        updateData['createdBy'] = 'admin'
        updateData['createdDate'] = datetime.now(timezone.utc)
        theApp = IOTApp(**updateData)
        theApp.createdDate = str(theApp.createdDate.strftime('%Y-%m-%d %H:%M:%S'))
        apps_db.insert(theApp)
        return theApp