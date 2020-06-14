'''
Created on 30.05.2020

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
import datetime
import argparse

from com.github.c2nes.javalang import parser

from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from de.mindscan.fluentgenesis.bpe.bpe_encoder_decoder import SimpleBPEEncoder
from de.mindscan.fluentgenesis.dataprocessing.method_dataset import MethodDataset
from de.mindscan.fluentgenesis.dataprocessing.method_extractor import tokenize_file, extract_allmethods_from_compilation_unit

# this might be a bad implementation, but it is good enough
def split_methodbody_into_multiple_lines(method_body):
    result = []
    current_line_number = -1
    current_line_tokens = []
    for token in method_body:
        token_line = token.position[0]
        
        if token_line != current_line_number:
            current_line_number = token_line
            if len(current_line_tokens) != 0:
                result.append(current_line_tokens)
                current_line_tokens = []
        current_line_tokens.append(token.value)
        pass
    if len(current_line_tokens) !=0:
        result.append(current_line_tokens)
        pass
    return result

def process_source_file(dataset_directory, source_file_path, encoder, dataset):
    # derive the full source file path
    full_source_file_path = os.path.join( dataset_directory, source_file_path);
    
    # Work on the source file
    java_tokenlist = tokenize_file(full_source_file_path)
    parsed_compilation_unit = parser.parse(java_tokenlist)
    
    # collect file names, line numbers, method names, class names etc  
    all_methods_per_source = extract_allmethods_from_compilation_unit(parsed_compilation_unit, java_tokenlist)
    
    for single_method in all_methods_per_source:
        try:
            method_name = single_method['method_name']
            method_class_name = single_method['class_name']
            method_body = single_method['method_body']
            method_signature = single_method['method_signature']
            
            multi_line_body = split_methodbody_into_multiple_lines(method_body)
            
            # encode body code and methodnames using the bpe-vocabulary
            bpe_encoded_methodname = encoder.encode( [ method_name ] )
            bpe_encoded_methodbody_ml = encoder.encode_multi_line( multi_line_body )
            bpe_encoded_signature = encoder.encode ( [ token.value for token in method_signature ] )
            
            # do some calculations on the tokens and on the java code, so selection of smaller datasets is possible
            bpe_encoded_method_name_length = len(bpe_encoded_methodname)
            bpe_encoded_method_body_length = sum([len(line) for line in bpe_encoded_methodbody_ml])
            bpe_encoded_method_sig_length = len(bpe_encoded_signature)
            
            # save this into dataset
            method_data = { 
                "source_file_path": source_file_path,
                "method_class_name": method_class_name,
                "method_name": method_name,
                "encoded_method_name_length": bpe_encoded_method_name_length,
                "encoded_method_name": bpe_encoded_methodname,
                "encoded_method_body_length": bpe_encoded_method_body_length,
                "encoded_method_body": bpe_encoded_methodbody_ml,
                "encoded_method_sign_length": bpe_encoded_method_sig_length,
                "encoded_method_sign": bpe_encoded_signature,
                "method_body": method_body 
                }
            dataset.add_method_data( method_data )
        except:
            # ignore problematic method
            pass

def walkFiles(path):
    filenames = []
    for root, _, files in os.walk(path):
        for file_ in files:
            if not file_.endswith(".java"):
                continue
            filenames.append(os.path.realpath(os.path.join(root, file_)))
    return filenames


def process_all_source_files(dataset_directory, encoder, method_dataset):
    time_at_start = datetime.datetime.now()

    print( "===[ Start ]===")
    print( "time at start: " + str(time_at_start))

    filenames = walkFiles(dataset_directory)
    
    time_after_walkingfiles = datetime.datetime.now()
    
    print( "time after walking files: " + str(time_after_walkingfiles))

    print( "===[ Encode ]===")
    
    for current_source_filename in filenames:
        try:
            print(current_source_filename)
            process_source_file('', current_source_filename, encoder, method_dataset)
        except:
            # ignore files , which cause any problem - we can deal with them much later.
            pass
    
    time_after_encoding = datetime.datetime.now()
    
    # print some statistics
    print( "===[ The End ]===")
    print( "time at start: " + str(time_at_start))
    print( "time after walking files: " + str(time_after_walkingfiles))
    print( "time when ready_encoding: " + str(time_after_encoding))


def doWork(bpe_model_name, bpe_directory, dataset_directory, output_filename):
    model = BPEModel(bpe_model_name, bpe_directory)
    model.load_hparams()
    
    # dataset_directory = 'D:\\Downloads\\Big-Code-full\\'
    # dataset_directory = 'D:\\Downloads\\Big-Code-excerpt\\'
    # dataset_directory = model.get_data_source_path()
    
    # only one class in compilation unit
    # some_source_filename = 'java_projects\\Algorithms\\src\\org\\rekdev\\trees\\BinaryTreeNode.java'
    
    # has multiple classes parallel in one compilation unit
    # some_source_filename = 'java_projects\\CSSMin\\CSSMin.java'
    
    # nested classes
    # some_source_filename = 'java_projects\\cvs-plugin\\\src\\\main\\\java\\\hudson\\\scm\\CVSChangeLogSet.java'

    # inner and/or anonymous classes
    # TODO: anonymous inner classes won't be recognized as ClassDeclaration / ClassCreator kann im Body auch methodendeklarationen enthalten
    # some_source_filename = 'java_projects\\emf\\plugins\\org.eclipse.emf.codegen\\src\\org\\eclipse\\emf\\codegen\\CodeGen.java'
    
    model_vocabulary = model.load_tokens()
    model_bpe_data = model.load_bpe_pairs()
    
    encoder = SimpleBPEEncoder(model_vocabulary, model_bpe_data)
    
    method_dataset = MethodDataset(dataset_name=output_filename)
    method_dataset.prepareNewDataset(dataset_directory)
    
    # now crawl the directory and process each file...
    process_all_source_files(dataset_directory, encoder, method_dataset)
    
    method_dataset.finish()
    pass


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create the method "NextLine"-Dataset.')
    
    parser.add_argument('--dataset-dir', dest='dataset_directory', help='Path to the dataset (must include tailing directory separators)', default='D:\\Downloads\\Big-Code-excerpt\\' )
    parser.add_argument('--bpe-model-dir', dest='bpe_model_directory', help='Path to the BPE directory containing the Model folder', default='../bpe/')
    parser.add_argument('--bpe-model', dest='bpe_model', help='the BPE-Model to use e.g. "16K-full"', default='16K-full')
    parser.add_argument('--output-filename', dest='output_name', help='the filename fo the jsonl-output', default='methodNextLineDataset.jsonl')
    
    args = parser.parse_args()
    
    print(args)
    
    doWork(bpe_model_name = args.bpe_model, 
           bpe_directory = args.bpe_model_directory, 
           dataset_directory = args.dataset_directory, 
           output_filename = args.output_name )
    
    pass