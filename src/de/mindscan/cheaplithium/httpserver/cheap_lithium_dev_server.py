'''
Created on 21.11.2020

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

@autor: Maxim Gansert, Mindscan
'''
import sys
sys.path.insert(0,'../../../../../src')

import json
import uuid as uid
import os.path

from fastapi import FastAPI, Form

app = FastAPI()

DATAMODEL_DIR = '../../../../../data/cheaplithium/dm/'



# DecisionModel "Database"
# persist only as long as the server is runing, for development, we don't need database support 
decisionModelDatabase = {}

# -----------------------------------------
# Later extract the decision modelling code
# -----------------------------------------
def create_successful_uuid_result(uuid:str):
    return {"uuid":uuid, "isSuccess":True, "isError":False}

# --------------------------------------



# --------------------------------------
# API-Webserver "code" - 
# --------------------------------------

@app.get("/")
def read_root():
    return {"message":"Hello World! It works! But now, go away!"}

@app.get("/CheapLithium/rest/getDecisionModel/{uuid}")
async def provide_decision_model( uuid:str='0518f24f-41a0-4f13-b5f6-94a015b5b04c'):
    try:
        read_uuid = uid.UUID('{' + uuid + '}')
    except:
        return {"messsage":"invalid uuid"}
    
    if ( str(read_uuid) == uuid):
        jsonfilepath = DATAMODEL_DIR + str(read_uuid) + '.json'

        if uuid in decisionModelDatabase:
            return decisionModelDatabase[uuid]
        else:
            if os.path.isfile(jsonfilepath):
                with open(jsonfilepath) as json_source_file:
                    tmpDecisionModel = json.load(json_source_file)
                    decisionModelDatabase[uuid] = tmpDecisionModel
                    return tmpDecisionModel
            else:
                # try to load model from hash-map - for "updated" models then load from hashmap first.
                abs_name = os.path.abspath(jsonfilepath)
                return {"message":"no_such_file "+str(abs_name)}
    else:
        return  {"message":"uuid doesn't match."}
    
    return {}

@app.post("/CheapLithium/rest/createDecisionModel")
async def create_decision_model( name:str = Form(...), displayname:str=Form(...), 
    description:str=Form(...), version:str = Form(...)):
    
    uuid = uid.uuid4()
    # create a model with a start and an end node, using generated model uuid
    
    return create_successful_uuid_result(uuid)


@app.post("/CheapLithium/rest/updateDecisionModel")
async def update_decision_model(uuid: str = Form(...), name:str = Form(...),  displayname:str=Form(...), 
    description:str=Form(...), version:str = Form(...)):
    # update that model in the dictionary... - no persistence required
    return create_successful_uuid_result(uuid)


@app.post("/CheapLithium/rest/cloneDecisionModel")
async def clone_decision_model(uuid: str = Form(...)):
    # clone/copy that model, but create different uuids for each element
    # clone that model in the dictionary... - no persistence required 
    
    return create_successful_uuid_result(uuid)
