from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import Form, Body
import wmi
import pythoncom
from Api import Getvm
from typing import Union
from pydantic import BaseModel
from Controller import code

router = APIRouter(prefix='/get')

class Item(BaseModel):
    id_d: str = None
    toekn: str
    data: str = None

@router.post('/*')
def check(data):
    if not data != code.read('server')['toekn']:
        return {"code": "-1", "msg": "toekn校验错误"}
    APP.include_router(Getvm.router)