'''
Created on 31.08.2019

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

import os
import json
import datetime

def read_hparams(model):
    with open(os.path.join("Model",model,"hparams.json"), 'r') as paramfile_file:
        hparams = json.load(paramfile_file)
        return hparams
    
    
class SimpleBPEEncoder(object):
    '''
    Byte pair encoder for source code / and of course texts (depends on the tokens/dictionary provided)
    '''
    
    def __init__(self, encoder_token_table):
        '''
        Constructor
        '''
        
        # Source Code tokens into indexes table
        self.__encoder_table = encoder_token_table
        # Indexed to Source Code tokens - invert the encoder table (see Stackoverflow q:483666) 
        self.__decoder_table = {value: key for key, value in encoder_token_table.items()}
    
    
    def encode(self, tokens):
        pass


    def decode(self, tokens):
        pass

def run_me(model_name):
    hparams = read_hparams(model_name)
    
    time_at_start = datetime.datetime.now()
    print( "time at start: " + str(time_at_start))
    
    bpe_encoder = SimpleBPEEncoder();

if __name__ == '__main__':
    # "1K-datapoint", "10K-excerpt", "16K-excerpt", "50K-full", "100K-full"
    model_name = "50K-full"
    
    run_me(model_name)

