'''
Created on 25.01.2020

MIT License

Copyright (c) 2019 Maxim Gansert

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

@author: Maxim Gansert, Mindscan
'''
from com.github.c2nes.javalang import tokenizer

class MethodDataset(object):
    '''
    classdocs
    '''

    def __init__(self, params=None):
        '''
        Constructor
        '''
        pass
    
    def prepareNewDataset(self):
        pass
    
    def finish(self):
        pass
        
    def add_method_data(self, params):
        print("==["+params['method_name']+" / "+params['method_class_name']+"]==")
        print("bpe_method_name["+str(params['encoded_method_name_length'])+"] = " + str(params['encoded_method_name']))
        print("bpe_body["+str(params['encoded_method_body_length'])+"] = " + str(params['encoded_method_body']))
        
        print(tokenizer.reformat_tokens(params['method_body']))
        pass
    
