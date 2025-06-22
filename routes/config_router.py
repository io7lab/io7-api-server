from typing import List
from fastapi import APIRouter, HTTPException, Body, Depends, status

from models import ConfigVar
from secutils import authenticate
from environments import Database

config_db = Database('config_var')
router = APIRouter(tags=['Config'])

@router.get('/', response_model=List[ConfigVar])
async def get_configs(jwt: str = Depends(authenticate)) -> List[ConfigVar]:
    """
    Retrieve all configuration variables.
    
    This endpoint returns the io7 platform configuration variables.
    Authentication is required to access this endpoint.
    
    Returns:
    - A list of all customizable configuration variables.
    """
    return config_db.getAll()

@router.get('/{key}')
async def get_var(key: str, jwt: str = Depends(authenticate)) -> ConfigVar:
    """
    Retrieve a configuration variable.
    
    This endpoint returns the io7 platform configuration variable requested by key.
    Authentication is required to access this endpoint.
    
    Parameters:
    - key: the configuration variable name
    
    Returns:
    - The configuration variable value
    """
    value =  config_db.getOne(config_db.qry.key == key)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no configuration variable ({key})"
    )
    return value 

@router.put('/')
async def set_configs(vars: List[ConfigVar], jwt: str = Depends(authenticate)) -> dict:
    """
    Register all customizable configuration variables.
    
    This endpoint sets all configuration variables. 
    Authentication is required to access this endpoint.
    
    Parameters:
    - vars: a list of configuration variable key-value pairs

    Caution:
    This is a destructive operation since existing variables will be deleted if not included in `vars`.
    
    Returns:
    - A JSON object with processing status.
    """ 
    all_vars = config_db.getAll()
    for var in all_vars:
        config_db.delete(config_db.qry.key == var['key'])
    try:
        for var in vars:
            config_db.insert(ConfigVar(key=var.key, value=var.value))
        return {"status":"ok"}
    except Exception as e:
        return {"status":"error", "Exception": type(e).__name__}


@router.patch('/')
async def update_configs(vars: List[ConfigVar], jwt: str = Depends(authenticate)) -> dict:
    """
    Update customizable configuration variables with the provided data.
    
    This endpoint updates the given variables in the `vars` list to new values.
    Authentication is required to access this endpoint.
    
    Parameters:
    - vars: a list of configuration variable key-value pairs

    Caution:
    This is an incremental update since it only updates the given variables, keeping the others intact.
    
    Returns:
    - A JSON object with processing status.
    """
    try:
        for var in vars:
            config_db.insert(ConfigVar(key=var.key, value=var.value))
        return {"status":"ok"}
    except Exception as e:
        return {"status":"error", "Exception": type(e).__name__}

@router.put('/{key}')
async def update_var(
    key: str, 
    var: dict = Body(
        ...,
        example= {
            "value" : "theValue"
        }
    ), jwt: str = Depends(authenticate)) -> dict:
    """
    Updates the configuration variable matching the `key`.
    
    This endpoint updates the configuration variable with the specified key.
    Authentication is required to access this endpoint.
    
    Parameters:
    - key: the configuration variable name
    - var: the configuration variable value json
    
    Returns:
    - A JSON object with processing status.
    """
    if "value" not in var:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'value' field in request body"
        )
    try:
        config_db.insert(ConfigVar(key=key, value=var['value']))
        return {"status":"ok"}
    except Exception as e:
        return {"status":"error", "Exception": type(e).__name__}


@router.delete('/{key}')
async def del_var(key: str, jwt: str = Depends(authenticate)) -> dict:
    """
    Delete the configuration variable matching the `key`.
    
    This endpoint removes the configuration variable with the specified key.
    Authentication is required to access this endpoint.
    
    Caution:
    - This operation cannot be undone
    
    Parameters:
    - key: the configuration variable name
    
    Returns:
    - A confirmation message with the processing status
    """
    value = config_db.getOne(config_db.qry.key == key)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no configuration variable ({key})"
        )
    try:
        config_db.delete(config_db.qry.key == key)
        return {"status":"ok"}
    except Exception as e:
        return {"status":"error", "Exception": type(e).__name__}
