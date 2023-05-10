from fastapi import APIRouter
from fastapi import FastAPI, Request
from fastapi import Form, Body
import wmi
import pythoncom
from typing import Union
from pydantic import BaseModel
from Controller import code
import json
import subprocess

APP = FastAPI()
router = APIRouter(tags=['api'])


class Name(BaseModel):
    toekn: str
    id_d: str
    new_name: str
    checkpoint_name: str
    data: str
    
class Toekn(BaseModel):
    toekn: str
    
class Get(BaseModel):
    toekn: str
    id_d: str

class Config(BaseModel):
    toekn: str
    id_d: str
    cpu_count: str
    memory_size: str
    data: str
    
class Iso(BaseModel):
    toekn: str
    id_d: str
    iso: str

class Xiso(BaseModel):
    toekn: str
    id_d: str
    
@router.post('/all_vm', tags=['api'], include_in_schema=False)
def get_all(toekn: Toekn):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem()
    information = {}
    for vm_count in vm:
        if vm_count.Caption == '虚拟机':
            if vm_count.EnabledDefault == 2:
                state = '运行'
            elif vm_count.EnabledDefault == 3:
                state = '关机'
            elif vm_count.EnabledDefault == 4:
                state = '正在关机'
            elif vm_count.EnabledDefault == 10:
                state = '正在启动'
            elif vm_count.EnabledDefault == 11:
                state = '正在重启'
            else:
                state = '未知'
            information[vm_count.Name] = {
                'name': vm_count.ElementName,
                'state': state
            }
    return information
    
#@router.post('/get_name', tags=['api'])
def get_name(id_d):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=id_d)
    return vm[0].ElementName
    
@router.post('/compound')
def compound(config: Config):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm_memory = con.Msvm_MemorySettingData()
    vm_cpu = con.Msvm_ProcessorSettingData()
    for vm_cpu_count in vm_cpu:
        if vm_cpu_count.Description == 'Microsoft 虚拟处理器的设置。':
            id_d = auxiliary.get_middle_text(vm_cpu_count.InstanceID, 'Microsoft:', '\\')
            if id_d in data:
                config.cpu_count = int(vm_cpu_count.VirtualQuantity)
    for vm_memory_count in vm_memory:
        if vm_memory_count.Description == 'Microsoft 虚拟机内存的设置。':
            id_d = auxiliary.get_middle_text(vm_memory_count.InstanceID, 'Microsoft:', '\\')
            if id_d in data:
                config.memory_size = int(vm_memory_count.VirtualQuantity)
    return data
    
@router.post('/existence')
def existence(get: Get):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=get.id_d)
    if len(vm) == 0:
        return False
    return True

@router.post('/get_state')
def get_state(get: Get):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=get.id_d)

    if len(vm) == 0:
        return False
    
    vm = vm[0]
    if vm.EnabledDefault == 2:
        state = '运行'
    elif vm.EnabledDefault == 3:
        state = '关机'
    elif vm.EnabledDefault == 4:
        state = '正在关机'
    elif vm.EnabledDefault == 10:
        state = '正在启动'
    elif vm.EnabledDefault == 11:
        state = '正在重启'
    else:
        state = '未知'
    return state

@router.post('/revise_config')
def revise_config(get: Get):
    name = get_name(Get.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Set-VMProcessor -VMName "{name}" -Count {item.cpu_count};Set-VMMemory -VMName "{name}" -StartupBytes {item.memory_size}MB'], shell=True)
    except Exception:
        return False
    else:
        return True

@router.post('/start')
def start(get: Get):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=get.id_d)
    
    if len(vm) == 0:
        return False
    
    vm[0].RequestStateChange(2)
    return True

@router.post('/shutdown')
def shutdown(get: Get):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=get.id_d)
    
    if len(vm) == 0:
        return False
    
    vm[0].RequestStateChange(3)
    return True

@router.post('/force_shutdown')
def force_shutdown(get: Get):
    name = get_name(get.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Stop-VM -Name "{name}" –Force'], shell=True)
    except Exception:
        return False
    else:
        return True

@router.post('/restart')
def restart(get: Get):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=get.id_d)
    
    if len(vm) == 0:
        return False
    
    vm[0].RequestStateChange(10)
    return True

@router.post('/rename')
def rename(name: Name):
    old_name = get_name(name.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Rename-VM "{old_name}" "{name.new_name}"'], shell=True)
    except Exception:
        return False
    else:
        return True

@router.post('/get_checkpoint')
def get_checkpoint(get: Get):
    pythoncom.CoInitialize()
    con = wmi.WMI(wmi=wmi.connect_server(server='127.0.0.1', namespace=r'root\virtualization\v2'))
    vm = con.Msvm_ComputerSystem(Name=get.id_d)
    
    if len(vm) == 0:
        return False
    
    vm = vm[0]
    checkpoint = vm.associators(wmi_result_class='Msvm_VirtualSystemSettingData')
    information = []
    name = get_name(get.id_d)
    for checkpoint_count in checkpoint:
        information.append(checkpoint_count.ElementName)
    if information == [name]:
        information.clear()
    else:
        information.remove(name)
        information = list(set(information))
    return information

@router.post('/apply_checkpoint')
def apply_checkpoint(get: Get, name: Name):
    name = get_name(get.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Get-VMSnapshot "{name}" "{name.checkpoint_name}" | Restore-VMSnapshot -Confirm:$false'], shell=True)
    except Exception:
        return False
    else:
        return True
    
@router.post('/naw_apply_checkpoint')
def naw_apply_checkpoint(get: Get):
    name = get_name(get.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Checkpoint-VM "{name}"'], shell=True)
    except Exception:
        return False
    else:
        return True

@router.post('/iso')
def iso(toekn: Toekn):
    import os
    
    data = code.read('config')
    path = data['path']
    
    return os.listdir(path)
    
@router.post('/giso')
def giso(iso: Iso):
    import os
    
    data = code.read('config')
    path = data['path']
    
    name = get_name(iso.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Get-VM "{name}" | Get-VMDVDDrive | Set-VMDvdDrive -Path "{path}\\{iso.iso}"'], shell=True)
    except Exception:
        return False
    else:
        return True

@router.post('/xiso')
def giso(xiso: Xiso):
    
    name = get_name(xiso.id_d)
    try:
        subprocess.check_output(['powershell.exe', f'Get-VM "{name}" | Get-VMDVDDrive | Set-VMDvdDrive –Path $Null'], shell=True)
    except Exception:
        return False
    else:
        return True

@router.get('/vnc/{id_d}')
def vnc(id_d):
    
    import requests
    z = requests.get("http://127.0.0.1:8080")
    name = get_name(id_d)
    
    
    url = "http://127.0.0.1:8080/?vcc="+id_d+"|administrator|127.0.0.1|zeidc!!!111"
    
    r = requests.get(url)

    return r.content
    #return url

@router.post('/text')
def text(get: Get):
    return get