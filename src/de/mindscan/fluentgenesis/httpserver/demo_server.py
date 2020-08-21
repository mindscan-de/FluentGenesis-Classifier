'''
Created on 16.08.2020

MIT License

Copyright (c) 2020 Maxim Gansert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@author: JohnDoe
'''
import sys
from pyparsing import Optional
sys.path.insert(0,'../../../../../src')

import random

from fastapi import FastAPI, Form
from pydantic import BaseModel

from de.mindscan.fluentgenesis.httpserver.demo_server_utils import predictTheMethodName

# run with uvicorn demo_server:app --reload
app = FastAPI()
    
@app.get("/")
def read_root():
    return {"message":"Hello World! It works!"}

source = [
    # Channel#updatePlayer,
    'if (add) \n\
        this.playerList.add(player); \n\
    else \n\
        this.playerList.remove(player); \n\
    return this.containsPlayer(player);',
    
    # CHennel#containsPlayer
    'return this.playerList.contains(player);',
    
    'this.z = z;',
    
    'return TypeID;',
    
    'return new StructureBlock(x, y, z, TypeID, SubID);',
    
    'return this.z + ":" + this.x;'
    
    ] * 3

@app.on_event("startup")
async def startup_event():
    # instantiate the model / instantiate the preoxy server
    pass
    
@app.on_event("shutdown")
async def shutdown_event():
    # close the model / close tensorflow / close the proxy server
    pass

@app.get("/heartbeat")
async def heartbeat_request():
    # provide an answer the plugin expects to find out, whether the service is running
    return {'alive':'true'}


## TODO: cache the results and serve the cached results
## ----------------------------------------------------
## Maybe do some caching on the serverside, for repeating requests
## especially if more users are using this service
##

@app.get("/predictMethodNames/{max_count}")
async def predict_method_name( max_count:int=5):
    max_count = min( max_count, 10 )
    # read the source from the request.
    theSource = random.choice( source )
    
    return predictTheMethodName( theSource, max_count )[:max_count]

@app.post("/predictMethodNamesP/{max_count}")
async def predict_method_namep( max_count:int=5, body: str = Form(...)):
    max_count = min( max_count, 10 )
    # read the source from the request.
    theSource = body
    
    return predictTheMethodName( theSource, max_count )[:max_count]

