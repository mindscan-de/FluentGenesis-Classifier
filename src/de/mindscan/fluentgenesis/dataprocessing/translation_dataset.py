'''
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

Created on 16.09.2020

@autor: Maxim Gansert, Mindscan
'''

import os

class TranslationDataset(object):
    '''
    classdocs
    '''


    def __init__(self, dataset_name = None):
        '''
        Constructor
        '''
        self.__dataset_name = 'translationDataset.jsonl' if dataset_name is None else dataset_name
        self.__filehandle_to = None
        self.__filehandle_from = None
        pass
        
    def prepareNewDataset(self, dataset_directory):
        fullFileNameFrom = os.path.join(dataset_directory, self.__dataset_name + ".from")
        fullFileNameTo = os.path.join(dataset_directory, self.__dataset_name + ".to")
        
        self.__filehandle_from = open(fullFileNameFrom, 'w')
        self.__filehandle_to = open(fullFileNameTo, 'w')
    
    def finish(self):
        if self.__filehandle_from is not None:
            self.__filehandle_from.flush()
            self.__filehandle_from.close()
            self.__filehandle_from = None
            
        if self.__filehandle_to is not None:
            self.__filehandle_to.flush()
            self.__filehandle_to.close()
            self.__filehandle_to = None
        
        
    def addTranslation(self, translation_from, translation_to):
        pass
    
    
    