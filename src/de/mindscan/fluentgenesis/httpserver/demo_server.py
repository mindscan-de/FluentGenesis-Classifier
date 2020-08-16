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

from fastapi import FastAPI, Form
from pydantic import BaseModel

# run with uvicorn demo_server:app --reload
app = FastAPI()

class Prediction(BaseModel):
    name: str
    price: float
    if_offer: bool = None
    
@app.get("/")
def read_root():
    return {"message":"Hello World! It works!"}

#@app.post("/predictMethodNames/{maxCount}")
#async def predict_method_name( maxCount:int=5, methodBody: str = Form(...), className: str=Form(...)):
@app.get("/predictMethodNames/{max_count}")
async def predict_method_name( max_count:int=5):

    # split into tokens
    # bpe-encode tokenized code
    
    max_count = min(max_count,10)
    
    # either predict using tensorflow.serving
    # or predict using loaded model itself
    
    # process answer and not more than 10 methodnames allowed and replace them
    result = ['getName', 'getId', 'getNamedId', 'calculateName', 'name',
              'createId', 'toString', 'toName', 'convertName', 'convert','neverRETURNThis']
    
    # return array of k method names
    return result[:max_count]
    