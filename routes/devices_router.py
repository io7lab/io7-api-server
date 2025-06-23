from typing import List
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Body
from datetime import timezone, timedelta, datetime
from secutils import authenticate
from models import Device, NewDevice, IOTApp, FirmwareInfo
from dynsec.devices_dynsec import add_dynsec_device, delete_dynsec_device
from dynsec.roles_dynsec import delete_dynsec_role
from dynsec.devices_actions import reboot_device_action, reset_device_action, update_metadata_action, upgrade_firmware_action
from environments import Settings, Database, dynsec_all_devices, dynsec_get_device

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

device_db = Database(Device.Settings.name)
apps_db = Database(IOTApp.Settings.name)
router = APIRouter(tags=['Devices'])

@router.get('/{devId}/reboot')
async def reboot_device(devId: str, jwt: str = Depends(authenticate)) -> dict:
    """
    Remotely reboot a device by its ID.
    
    This endpoint sends a reboot command to the specified device.
    Authentication is required to access this endpoint.
    
    Caution:
    - The device will become temporarily unavailable during reboot
    - Any active operations on the device will be interrupted
    - Ensure the device is not performing critical tasks before rebooting
    
    Parameters:
    - devId: The unique identifier of the device to reboot
    
    Returns:
    - Confirmation message of the reboot command
    """
    device = device_db.getOne(device_db.qry.devId == devId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device(devId:{devId}) does not exist"
        )
    reboot_device_action(devId)
    return {"message": "Rebooting Device", "devId": devId}

@router.get('/{devId}/reset')
async def reset_device(devId: str, jwt: str = Depends(authenticate)) -> dict:
    """
    Reset a device to factory settings by its ID.
    
    This endpoint sends a factory reset command to the specified device.
    Authentication is required to access this endpoint.
    
    Caution:
    - This is a destructive operation that cannot be undone
    - All device configurations, data, and settings will be erased
    - The device will need to be reconfigured after reset
    - Only use this operation when absolutely necessary
    
    Parameters:
    - devId: The unique identifier of the device to factory reset
    
    Returns:
    - Confirmation message of the reset command
    """
    device = device_db.getOne(device_db.qry.devId == devId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device(devId:{devId}) does not exist"
        )
    reset_device_action(devId)
    return {"message": "Factory Resetting Device", "devId": devId}

@router.put('/{devId}/updateMeta')
async def update_metadata(devId: str, metaData: dict, jwt: str = Depends(authenticate)) -> dict:
    """
    Update the metadata for a specific device.
    
    This endpoint allows updating device metadata such as pubInterval, location, tags, or other attributes.
    Authentication is required to access this endpoint.
    
    Caution:
    - Ensure that the metadata format conforms to expected schema
    - Metadata changes may affect device behavior in applications
    
    Parameters:
    - devId: The unique identifier of the device to update
    - metaData: Dictionary containing the metadata to update
    
    Returns:
    - Confirmation message of the metadata update command
    """
    qryDevice = device_db.getOne(device_db.qry.devId == devId)
    if not qryDevice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device(devId:{devId}) does not exist"
        )
    update_metadata_action(devId, metaData)
    return {"message": "Metadata being updated", "devId": devId}

@router.put('/{devId}/upgrade')
async def upgrade_firmware(devId: str, fwInfo: FirmwareInfo, jwt: str = Depends(authenticate)) -> dict:
    """
    Upgrade the firmware of a specific device.
    
    This endpoint triggers a firmware upgrade for the specified device using the provided firmware URL.
    Authentication is required to access this endpoint.
    
    Caution:
    - Ensure the firmware URL is secure (HTTPS) and trusted
    - Firmware upgrades may cause device downtime
    - Incorrect firmware can permanently damage the device
    - Always ensure firmware compatibility before upgrading
    - Do not interrupt the upgrade process once started
    
    Parameters:
    - devId: The unique identifier of the device to upgrade
    - fwInfo: Object containing the firmware URL and other information
    
    Returns:
    - Confirmation message of the firmware upgrade command
    """
    qryDevice = device_db.getOne(device_db.qry.devId == devId)
    if not qryDevice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device(devId:{devId}) does not exist"
        )
    upgrade_firmware_action(devId, fwInfo.fw_url)
    return {"message": "Firmware being upgraded", "devId": devId}

@router.get('/{devId}', response_model=Device)
async def get_device(devId: str, jwt: str = Depends(authenticate)) -> Device:
    """
    Retrieve details for a specific device by ID.
    
    This endpoint returns all information about the device with the specified ID.
    Authentication is required to access this endpoint.
    
    Parameters:
    - devId: The unique identifier of the device to retrieve
    
    Returns:
    - A Device object containing all device details
    """
    device = device_db.getOne(device_db.qry.devId == devId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device(devId:{devId}) does not exist"
        )
    return device

@router.delete('/{devId}')
async def del_device(devId: str, jwt: str = Depends(authenticate)) -> dict:
    """
    Delete a device from the system.
    
    This endpoint completely removes a device from the database and MQTT infrastructure.
    For gateway devices, it also removes all associated edge devices.
    Authentication is required to access this endpoint.
    
    Caution:
    - This operation cannot be undone
    - For gateway devices, all connected edge devices will also be deleted
    - All device access permissions will be permanently removed
    - Any services depending on this device will stop working
    - Deleting a gateway will delete all the Edge devices it created
    
    Parameters:
    - devId: The unique identifier of the device to delete
    
    Returns:
    - Confirmation message with the deleted device ID
    """
    device  = device_db.getOne(device_db.qry.devId == devId)    # this should come before deletion
    doc_ids = device_db.delete(device_db.qry.devId == devId)
    if not doc_ids or len(doc_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device(devId:{devId}) does not exist"
        )
    if device['type'] == 'gateway':
        edges = device_db.get(device_db.qry.createdBy == devId)
        for edge in edges:
            device_db.delete(device_db.qry.devId == edge['devId'])
            delete_dynsec_role(edge['devId'])       # edge roles; edge devices consist of roles only
        delete_dynsec_role(devId)                   # gateway role
        delete_dynsec_device(devId)                 # gateway device
    elif device['type'] == 'edge':
        delete_dynsec_role(devId)
    else:
        delete_dynsec_device(devId)
        delete_dynsec_role(devId)
    return {"message": "Device deleted successfully", "devId": devId}

# Returns Device objects with 'toFix' attribute, so return type is List[dict] instead of List[Device]
@router.get('/', response_model=List[dict])
async def get_devices(broken:bool = False, jwt: str = Depends(authenticate)) -> List[dict]:
    """
    Retrieve a list of all registered devices.
    
    This endpoint returns all devices registered in the system including gateways, edge devices, and regular devices.
    Authentication is required to access this endpoint.

    Cautions:
    - Device authentication & authorization is managed by the MQTT Dynamic Security Plugin
    - Device metadata is stored in the TinyDB database
    - Inconsistencies between these two data sources can result in broken device states
    - Use `?broken=true` to retrieve only devices with database/MQTT configuration mismatches
    
    Parameters:
    - broken: Optional argument to get the broken devices
    
    Returns:
    - A list of Device objects containing device details
    """
    if broken:
        dynsec_devices = dynsec_all_devices()
        db_devices = device_db.getAll()
        mal_dynsec_devices = []
        mal_db_devices = []
        for dyn_device in dynsec_devices:
            d = device_db.getOne(device_db.qry.devId == dyn_device)
            if d is None:
                db_d = Device(devId = dyn_device).dict()
                db_d['toFix'] = 'tinydb'
                mal_dynsec_devices.append(db_d)
        for db_device in db_devices:
            d = dynsec_get_device(db_device['devId'])
            if d is None:
                db_d = dict(db_device)
                db_d['toFix'] = 'dynsec'
                mal_db_devices.append(db_d)
        return(mal_db_devices + mal_dynsec_devices)
    else:
        device_list = []
        db_devices = device_db.getAll()
        for db_device in db_devices:
            d = dynsec_get_device(db_device['devId'])
            db_d = dict(db_device)
            if d is None and db_d['type'] != 'edge':
                db_d['toFix'] = 'dynsec'
            device_list.append(db_d)
        return device_list

@router.post('/')
async def add_device(newDevice: NewDevice, jwt: str = Depends(authenticate)) -> Device:
    """
    Register a new device in the system.
    
    This endpoint allows creation of new devices, edge devices, or gateways.
    Authentication is required to access this endpoint.
    
    Caution:
    - Device IDs cannot start with '$' or be named 'admin'
    - Device ID must be unique across both apps and devices
    - For edge devices, the createdBy field must reference a valid gateway
    - The device type must be one of 'gateway', 'edge', or 'device'
    - The password provided will be used for MQTT authentication
    
    Parameters:
    - newDevice: Object containing all required device information
    
    Returns:
    - The newly created Device object
    """
    if newDevice.devId.startswith('$') or newDevice.devId == 'admin':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The Id({newDevice.devId}) cannot be registered for Device/Gateway."
        )
    if not newDevice.type in ['gateway', 'edge', 'device']:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid Device Type({newDevice.type})"
        )
    qryDevice = device_db.getOne(device_db.qry.devId == newDevice.devId)
    qryApp = apps_db.getOne(apps_db.qry.appId == newDevice.devId)
    if qryDevice or qryApp:
        if qryApp:
            detail = f"The Id({newDevice.devId}) is already registered for AppId."
        else:
            detail = f"The Id({newDevice.devId}) is already registered for Device/Gateway."
        if type(jwt) == dict:
            # If jwt is a dict, then it means it is called by REST API
            # if not, it is called by MQTT
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=detail
            )
        else:
            logger.error(detail)
            return          # the device name for edge is already taken

    if newDevice.type == 'edge':
        gw = device_db.getOne(device_db.qry.devId == newDevice.createdBy)
        if not gw or gw['type'] != 'gateway':
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid Gateway({newDevice.createdBy})"
            )
    newDevice.createdDate = newDevice.createdDate.replace(tzinfo=timezone.utc)
    newDevice.createdDate = str(newDevice.createdDate.strftime('%Y-%m-%d %H:%M:%S'))
    device_db.insert(newDevice)
    add_dynsec_device(newDevice)
    return newDevice.dict()

@router.patch('/{devId}/update')
async def update_device(
    devId: str, updateData: dict = Body(
        {
            "password": "str",
            "type": "str",
            "devDesc": "str",
            "devMaker": "str",
            "devSerial": "str",
            "devModel": "str",
            "devHwVer": "str",
            "devFwVer": "str",
            "createdBy": "str"
        }
    ),
    jwt: str = Depends(authenticate)) -> Device:
    """
    Update device information and fix broken device states.
    
    This endpoint allows updating device metadata and fixing inconsistencies between the database
    and MQTT dynamic security configurations. It handles various scenarios including complete updates,
    password-only fixes for missing MQTT configurations, and database-only repairs.
    Authentication is required to access this endpoint.
    
    Caution:
    - Device IDs cannot start with '$' or be named 'admin'
    - Password is only allowed when recreating missing MQTT dynamic security configurations
    - Missing MQTT configurations will be recreated if password is provided
    - Device type must be one of 'gateway', 'edge', or 'device'
    
    Parameters:
    - devId: The unique identifier of the device to update
    - updateData: Dictionary containing the fields to update (password, type, devDesc, etc.)
    
    Returns:
    - The updated Device object with current information
    """
    if devId.startswith('$') or devId == 'admin':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = f"The Id({devId}) cannot be registered for Device/Gateway."
        )
    if 'type' in updateData and not updateData['type'] in ['gateway', 'edge', 'device']:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid Device Type({updateData['type']})"
        )

    db_device = device_db.getOne(device_db.qry.devId == devId)
    dyn_device = dynsec_get_device(devId)
    if db_device: 
        if dyn_device:
            # Both db_device & dyn_device found; update the information in TinyDB 
            if 'password' in updateData:
                # Filter out the password change since it's not allowed
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Device token cannot be changed"
                )
            else: 
                # Update the information in TinyDB
                for key, value in updateData.items():
                    if key in db_device:  # Only update existing keys
                        db_device[key] = value
                theDevice = Device(**db_device)
                theDevice.devId=devId
                theDevice.createdDate = str(theDevice.createdDate.strftime('%Y-%m-%d %H:%M:%S'))
                device_db.insert(theDevice)
                return theDevice
        elif 'password' in updateData:
            # No dyn_device found; create dyn_device
            db_device['password'] = updateData['password']
            newDevice = NewDevice(**db_device)
            add_dynsec_device(newDevice)
            return newDevice
        else:
            # No dyn_device found but can't create it since no password is given
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No change was made"
            )
    else:
        # dyn_device exists but no db_device found; filling in the information
        updateData['devId'] = devId
        updateData['createdBy'] = updateData['createdBy'] if 'createdBy' in updateData else 'admin'
        updateData['createdDate'] = datetime.now(timezone.utc)
        theDevice = Device(**updateData)
        theDevice.createdDate = str(theDevice.createdDate.strftime('%Y-%m-%d %H:%M:%S'))
        device_db.insert(theDevice)
        return theDevice