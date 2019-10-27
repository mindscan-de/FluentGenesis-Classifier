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

import datetime

from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from functools import lru_cache

@lru_cache(maxsize=65536)
def get_lexeme_pairs(word):
    lexeme_pairs = set()
    prev_lexeme = word[0]
    for current_lexeme in word[1:]:
        lexeme_pairs.add((prev_lexeme, current_lexeme))
        prev_lexeme = current_lexeme
    return lexeme_pairs


def build_replacement_key_for(token, first_mptl, next_mptl, joined):
    replacement_key=[]
    
    i=0
    while i<len(token):
        # copy all items to replacement_key before first_mptl & after
        try:
            j=token.index(first_mptl,i)
            replacement_key.extend(token[i:j])
            i=j
        except:
            replacement_key.extend(token[i:])
            break;
        
        if token[i] == first_mptl and (i+1)<len(token) and token[i+1] == next_mptl:
            # if next is next_mptl -> add joined to list
            replacement_key.append(joined)
            i+=2
        else:
            # if next is not next_mptl -> only the first_mptl 
            replacement_key.append(token[i])
            i+=1
    
    return tuple(replacement_key)

import ast

def translate(data):
    print(str(data).encode('utf-8'))
    for pair,_ in data.items():
        # print(str(pair).encode('utf-8'))
        # TODO: BUGGY -
        try:
            unserialized = ast.literal_eval(pair)
            return tuple(unserialized)
        except:
            print("cant do that...")
            return();
    return ()

    
class SimpleBPEEncoder(object):
    '''
    Byte pair encoder for source code / and of course texts (depends on the tokens/dictionary provided)
    '''
    
    def __init__(self, encoder_token_table, encoder_bpe_statistics):
        '''
        Constructor
        '''
        
        # Source Code tokens into indexes table
        self.__encoder_table = encoder_token_table
        # Indexed to Source Code tokens - invert the encoder table (see Stackoverflow q:483666) 
        self.__decoder_table = {value: key for (key, value) in encoder_token_table.items()}
        # Provide a cache to save reoccuring tokens.
        self.__bpe_cache = {}
        #
        self.__bpe_mp_lexemesIndex = { translate(data): int(index) for (index, data) in encoder_bpe_statistics.items() }
        
    
    
    def __isInBPECache(self, token):
        return token in self.__bpe_cache
    
    
    def __getFromBPECache(self, token):
        return self.__bpe_cache [ token ]
    
    
    def __putInBPECache(self, text_token, encoded_value):
        self.__bpe_cache[text_token] = encoded_value
    
    
    def __build_lexemes_for_token(self, token):
        # we do not need to transform this token, if it has a unique encoding in the table already. 
        # we also do not need to put a complete token into the cache
        if token in self.__encoder_table:
            return [ token ]
        
        # In case of encoding a file, we expect to find multiple occurences of the same token - so caching the individual exemes is an option
        if self.__isInBPECache( token ):
            return self.__getFromBPECache( token )
        
        # build charwise representation and lexeme pairs (starts with simple chars and extends to lexemes).
        word = tuple(token)
        word_char_pairs = get_lexeme_pairs( word )
        
        if not word_char_pairs:
            return [ token ]
        
        
        ## see also: "Random Access Data Compression" by Philip Gage, C/C++ User Journal, September 1997, Page 23--30
        ##
        ## Page 23 reads:
        ## >> "While (Compression is possible)"
        
        # transform the word, as long as it is encodeable / embeddable
        while True:
            ## -------------------------------------------
            ## >> "Find most frequent byte pair in buffer" 
            ## -------------------------------------------
            ## Since we make use of a precomuted statistics,
            ## and the statistics is ordered by occurence (most probable first) 
            ## we can look up the statistics, 
            ## and pick the one which is most used, 
            ## by finding the lexeme pair with the mininal index. 
            most_frequent_bpe_pair = min( word_char_pairs, key=( lambda pair: self.__bpe_mp_lexemesIndex.get( pair, float('inf') ) ) )
            
            # if we do not find an most probable byte pair / lexeme pair - there are no more combinings left and 
            # Compression is not more possible, so we must leave the outer loop.
            if most_frequent_bpe_pair not in self.__bpe_mp_lexemesIndex:
                break;
            
            ## ---------------------------------------------------
            ## >> "Add pair to table and assign it as unused byte"
            ## ---------------------------------------------------
            ## we do not think in bytes here but assign it an index, from a precomuted statistics
            
            ## replace all occurences
            first_mp_bp, next_mp_bp = most_frequent_bpe_pair
            word = build_replacement_key_for(word, first_mp_bp, next_mp_bp, "".join(most_frequent_bpe_pair))
            
            if len(word) == 1:
                break
            else:
                ## We replace the byte pairs with the new byte pairs after replacing (joining) pairs.
                ## and try next compression round continuing with
                ## ----------------------------------------
                ## "Find most frequent byte pair in buffer"
                ## ----------------------------------------
                word_char_pairs = get_lexeme_pairs( word )
                
        self.__putInBPECache(token, word)
        
        return word
    
    
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
        '''
        Decode a list of tokens of indexes of an embedding into a list of strings 
        '''
        decoded_tokens = []
        
        for token in tokens:
            decoded_tokens.append(self.__decoder_table[token])
        
        return decoded_tokens


def run_me(model):
    model_vocabulary = model.load_tokens()
    model_bpe_data = model.load_bpe_pairs()
    
    time_at_start = datetime.datetime.now()
    print( "time at start: " + str(time_at_start))
    
    # we must also make use of the vocabulary and the byte-pair occuences and pass that information to the encoder.
    bpe_encoder = SimpleBPEEncoder(model_vocabulary, model_bpe_data)
    
    importJava = bpe_encoder.encode(['import', 'java', ';'])
    importComGitubDatapoint = bpe_encoder.encode(['import', 'com','.','github','.','datapoint1', ';'])

    print(importJava)
    print(importComGitubDatapoint)
    
    print(bpe_encoder.decode(importJava))
    print(bpe_encoder.decode(importComGitubDatapoint))

if __name__ == '__main__':
    # "1K-datapoint", "10K-excerpt", "16K-excerpt", "50K-full", "100K-full"
    model = BPEModel("16K-excerpt")
    model.load_hparams()

    run_me(model)

