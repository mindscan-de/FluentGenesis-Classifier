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
        # Provide a cache to save reoccuring tokens.
        self.__bpe_cache = {}
    
    
    def __isInBPECache(self, token):
        return token in self.__bpe_cache
    
    
    def __getFromBPECache(self, token):
        return self.__bpe_cache [ token ]
    
    
    def __build_lexemes_for_token(self, token):
        # we do not need to transform this token, if it has a unique encoding in the table. 
        # we also do not need to put a complete token into the cache
        if token in self.__encoder_table:
            return [ token ]
        
        # In case of encoding a file, we expect to find multiple occurences of the same token - so caching the individual exemes is an option
        if self.__isInBPECache( token ):
            return self.__getFromBPECache( token ) 
        
        return []
    
    
    def encode(self, tokens):
        '''
        Encode a token list / token stream into a list of indexes of an embedding 
        '''
        
        encoded_tokens = []
        
        # instead of encoding a complete file / a method / a few lines of code on a character by character level, 
        # we can encode each token individually - A token can either be encoded into one lexeme or multiple lexemes (most frequent pairings)
        # 
        for token in tokens:
            # a token needs to be transformed into lexemes, which can be encoded into an embedding index. 
            bpe_lexemes=self.__build_lexemes_for_token( token )
            
            ## see also: "Random Access Data Compression" by Philip Gage, C/C++ User Journal, September 1997, Page 23--30
            ##
            ## Page 23 reads:
            
            ## >> "Replace all such pairs with this unused byte"
            ## let's think of "unused byte" with an index here 
            
            # replace the combined lexemes by their indexes 
            encoded_tokens.extend( self.__encoder_table[bpe_lexeme] for bpe_lexeme in bpe_lexemes )
        
        # return indexes for the embeddings
        return encoded_tokens


    def decode(self, tokens):
        pass


def run_me(model_name):
    hparams = read_hparams(model_name)
    
    time_at_start = datetime.datetime.now()
    print( "time at start: " + str(time_at_start))
    
    # we must also make use of the vocabulary and the byte-pair occuences and pass that information to the encoder.
    bpe_encoder = SimpleBPEEncoder([]);

if __name__ == '__main__':
    # "1K-datapoint", "10K-excerpt", "16K-excerpt", "50K-full", "100K-full"
    model_name = "50K-full"
    
    run_me(model_name)

