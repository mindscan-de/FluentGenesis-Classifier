'''
Created on 07.11.2020

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
sys.path.insert(0, '../../../../../src')

from de.mindscan.fluentgenesis.httpserver.labelling_server_utils import predictMultipleMethodNames

# run that with uvicorn labelling_server:app --reload
from fastapi import FastAPI, Form

app = FastAPI()

##
## Method names predictor, returns an array of (methodname with method_probability) items
## 
@app.post("/SilentFeedBackend/rest/predictMethodnames")
async def predict_method_names_from_body(maxPredictions: int = 16, methodBody:str = Form(...)):
    maxPredictions = min( maxPredictions, 32)
    predictedNames = predictMultipleMethodNames( methodBody, maxPredictions * 2 )[:maxPredictions]
    return {'numberOfMethodNames':len(predictedNames),
            'methodNamesItems': predictedNames }
