'''
Created on 19.10.2019

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

from _collections import OrderedDict

class BPEModel(object):
    '''
    classdocs
    '''

    def __init__(self, modelname):
        '''
        Constructor
        '''
        self.__model_directory = "Model"
        self.__model_name = modelname
        self.__hparams = {}
        self.read_hparams()
        
    def get_model_name(self):
        return self.__model_name
    
    def read_hparams(self):
        with open(os.path.join(self.__model_directory,self.__model_name,"hparams.json"), 'r') as paramfile_file:
            self.__hparams = json.load(paramfile_file)
            
        return self.__hparams
    
    def save_hparams(self, hparams=None):
        if hparams is None:
            hparams = self.__hparams
        
        with open(os.path.join(self.__model_directory, self.__model_name,"hparams.json"), 'w') as paramfile_file:
            json.dump(hparams, paramfile_file)
            
    def save_bpe_pairs(self, bpe_pairs_list):
        with open(os.path.join(self.__model_directory, self.__model_name, self.__hparams['token_bpefile']), 'w') as bpe_json_file:
            json.dump(bpe_pairs_list, bpe_json_file)
            
    def load_bpe_pairs(self):
        with open(os.path.join(self.__model_directory, self.__model_name, self.__hparams['token_bpefile']), 'r') as bpe_statistics_file:
            bpe_statistics = json.load(bpe_statistics_file)
            return bpe_statistics

    def save_tokens(self, bpe_tokens):
        with open(os.path.join(self.__model_directory, self.__model_name, self.__hparams['token_filename']), 'w') as json_file:
            json.dump(self.__sort_by_lexeme_value(bpe_tokens), json_file)
        
    def load_tokens(self):
        with open(os.path.join(self.__model_directory, self.__model_name, self.__hparams['token_filename']), 'r') as vocabulary_file:
            vocabulary = json.load(vocabulary_file)
            return vocabulary
    
    def get_global_tokenstatistics_path(self):
        return os.path.join(self.__model_directory, self.__model_name, self.__hparams['global_wordlist'])
    
    def __sort_by_lexeme_value(self, token_map):
        return OrderedDict(sorted(token_map.items(), key=lambda item:item[1] ))
