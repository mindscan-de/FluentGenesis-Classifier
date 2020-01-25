'''
Created on 25.01.2020

@author: JohnDoe
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
    
        
    def add_method_data(self, params):
        print("==["+params['method_name']+" / "+params['method_class_name']+"]==")
        print("bpe_method_name["+str(params['encoded_method_name_length'])+"] = " + str(params['encoded_method_name']))
        print("bpe_body["+str(params['encoded_method_body_length'])+"] = " + str(params['encoded_method_body']))
        
        print(tokenizer.reformat_tokens(params['method_body']))
        pass
    
