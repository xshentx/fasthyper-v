from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
from hashlib import md5
from Api import Getvm
from Controller import code
from Api import check

APP = FastAPI()
APP.include_router(Getvm.router, prefix='/api', tags=['api'])


@APP.middleware("http")
async def check(request: Request,call_next):

        data = await request.body()
        if request.method == "POST":
            #print(json.loads(data)['toekn')
            #toekn = json.loads(data.decode().replace("\n","").replace("\r","").replace(" ","").replace("b'",""))['toekn']
            if not data:
                return JSONResponse({"msg": "参数为空"},  status_code=400)
            if json.loads(data)['toekn'] != code.read('config')['toekn']:
                return JSONResponse({"msg": "toekn校验错误"},  status_code=400)
            async def request_body():
                return {'type': 'http.request',  'body': data,  'more_body': False}
            request = Request(request.scope,  request_body)
        
        response = await call_next(request)

        return response


def verify():
    data = code.read('config')
    if not data['server']['host']:
        data['server']['host'] = input("请输入host:")
        code.Write('config',data)
    if not data['server']['port']:
        data['server']['port'] = input("请输入port:")
        code.Write('config',data)
    if not data['toekn']:
        data['toekn'] = str(md5(input("请输入toekn:").encode('utf-8')).hexdigest())
        code.Write('config',data)
    if not data['path']:
        data['path'] = input("请输入path:")
        code.Write('config',data)
    
if __name__ == '__main__':
    verify()
    data = code.read('config')
    print("运行成功")
    uvicorn.run(APP, host=data['server']['host'], port=int(data['server']['port']))