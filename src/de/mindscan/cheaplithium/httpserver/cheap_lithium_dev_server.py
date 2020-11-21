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
import uuid
import os.path

from fastapi import FastAPI, Form

app = FastAPI()

DATAMODEL_DIR = '../../../../../data/cheaplithium/dm/'


@app.get("/")
def read_root():
    return {"message":"Hello World! It works! But now, go away!"}

@app.get("/getDecisionModel/{unique_id}")
async def provide_decision_model( unique_id:str='0518f24f-41a0-4f13-b5f6-94a015b5b04c'):
    dmdict ={}
    read_uuid = uuid.UUID('{' + unique_id + '}')
    
    if ( str(read_uuid) == unique_id):
        jsonfilepath = DATAMODEL_DIR + str(read_uuid) + '.json'
        if os.path.isfile(jsonfilepath):
            with open(jsonfilepath) as json_source_file:
                dmdict = json.load(json_source_file)
        else:
            abs_name = os.path.abspath(jsonfilepath)
            dmdict=  {"message":"no_such_file "+str(abs_name)}
    else:
        dmdict=  {"message":"uid doesn't match."}
    
    return dmdict
    
