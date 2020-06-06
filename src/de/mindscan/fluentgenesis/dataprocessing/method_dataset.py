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

import json
import os

# from com.github.c2nes.javalang import tokenizer

#
# Create, Save, Load and provide the MethodDataset 
# ------------------------------------------------
# Two Modes of operation:
## First (write only / overwrite)
### prepareNewDataset()
### add_method_data()[]
### finish()
#
## Second (read only) / maybe i will try a different approach like pandas/dataframe for loading.
### loadPreparedDataset
### provide an (resetable) iterator, so it can be iterated n/many times.
##

class MethodDataset(object):
    '''
    classdocs
    '''

    def __init__(self, dataset_name = None):
        '''
        Constructor
        '''
        self.__dataset_name = 'methodDataset.jsonl' if dataset_name is  None else dataset_name 
        self.__filehandle = None
        pass
    
    def prepareNewDataset(self, dataset_directory):
        fullFileName = os.path.join(dataset_directory, self.__dataset_name)
        self.__filehandle = open(fullFileName,'w')
    
    def loadDataset(self, dataset_directory):
        fullFileName = os.path.join(dataset_directory, self.__dataset_name)
        self.__filehandle = open(fullFileName,'r')
        
    def loadFilterSaveDataset(self, dataset_directory, applyfilter, output_suffix):
        fullFileName = os.path.join(dataset_directory, self.__dataset_name)
        fullOutFileName = os.path.join(dataset_directory+output_suffix, self.__dataset_name)
        
        self.__filehandle = open(fullFileName,'r')
        
        number_of_methods = 0;
        number_of_filtered_methods = 0
        
        with open(fullOutFileName,"w") as outputhandle:
            
            line, method_data = self._read_next_method_dataInternal()
            
            while method_data is not None:
                number_of_methods = number_of_methods + 1
                
                if number_of_methods % (256*1024) is 0:
                    print(str(number_of_methods / 1024) + "k methoden gefiltert.")
            
                # save the particular dataset to disk
                if applyfilter(method_data):
                    number_of_filtered_methods = number_of_filtered_methods + 1
                    # save the line to file... in different directory...
                    outputhandle.write(line)
                    
                line, method_data = self._read_next_method_dataInternal()
        
        print("processed "+str(number_of_methods)+ " # methods matching filter "+ str( number_of_filtered_methods))
        
    def read_next_method_data(self):
        if self.__filehandle is None:
            print("FileHandle is None")
            return
        
        #try:
        # eine Zeile lesen, diese Zeile, anschlieﬂend JSon deserialisieren
        line = self.__filehandle.readline()
        if not line:
            return None
        
        if line is "\n":
            return None
        
        #return line
        #json_string = line.decode("utf-8")
        return json.loads(line)
        #except:
        #    pass
    
    def _read_next_method_dataInternal(self):
        if self.__filehandle is None:
            print("FileHandle is None")
            return
        
        #try:
        # eine Zeile lesen, diese Zeile, anschlieﬂend JSon deserialisieren
        line = self.__filehandle.readline()
        if not line:
            return None, None
        
        if line is "\n":
            return line, None
        
        #return line
        #json_string = line.decode("utf-8")
        return line, json.loads(line)
        #except:
        #    pass
    
    def finish(self):
        if self.__filehandle is not None:
            self.__filehandle.flush()
            self.__filehandle.close()
        
    def add_method_data(self, params):
        if self.__filehandle is None:
            print("FileHandle is None")
            return
        
        method_entry = {
            'file_name': params['source_file_path'],
            'class_name': params['method_class_name'],
            'method_name': params['method_name'],
            'length_encoded_method_name': params['encoded_method_name_length'],
            'encoded_method_name': params['encoded_method_name'],
            'length_encoded_method_body': params['encoded_method_body_length'],
            'encoded_method_body': params['encoded_method_body']
            }
        
        try:
            print("==["+params['method_name']+" / "+params['method_class_name']+"]==")
            # print("bpe_method_name["+str(params['encoded_method_name_length'])+"] = " + str(params['encoded_method_name']))
            # print("bpe_body["+str(params['encoded_method_body_length'])+"] = " + str(params['encoded_method_body']))
            # print(tokenizer.reformat_tokens(params['method_body']))

        except:
            # in case we can not outut the class name or the method name
            pass
        
        try:
            json_string = json.dumps(method_entry)
            self.__filehandle.write(json_string)
            self.__filehandle.write("\n")
        except:
            # ignore errors, since we have millions of methods, we actually do not care yet.
            pass
        
    
