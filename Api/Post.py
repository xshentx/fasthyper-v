from pydantic import BaseModel

class toekn(BaseModel):
    toekn: str

class id_d(BaseModel):
    id_d: str

class data(BaseModel):
    data: str

class config(BaseModel):
    cpu_count: str
    memory_size: str
    
class name(BaseModel):
    new_name: str
    checkpoint_name: str