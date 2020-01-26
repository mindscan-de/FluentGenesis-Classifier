'''
Created on 17.01.2019

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

from com.github.c2nes.javalang import tokenizer, parser, ast
from com.github.c2nes.javalang.tree import ClassDeclaration

from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from de.mindscan.fluentgenesis.bpe.bpe_encoder_decoder import SimpleBPEEncoder

from method_dataset import MethodDataset

#
# Process the compilation unit
# ----------------------------
# 1. Tokenize the compilation unit
# 2. Find all classes in compilation unit 
##   Later
##   N2H - (interfaces and their default implementation)
##   N2H - (process more classes in a compilation unit (side by side)
# 3. Find/collect all classes in main-compilation unit class
##   Work through inner classes and work through methods
# 4. find methods for each class from previous step
# 5. process each method and add them to the dataset / process / encode
# 6. add them into a dataprocessing unit and save to disk / should work with millions of methods, maybe save after 100k methods everytime.

def extract_method_body ( tokens ):
    collect_mode = False
    extracted_body = []
    depth = 0
    for token in tokens:
        # don't collect the last closing brace token...
        if token.value is '}':
            depth-=1
            if depth is 0:
                collect_mode=False
                # break this loop, since all is done / we have more closing braces than opening braces.
                break
        
        if collect_mode:
            extracted_body.append(token)

        # don't collect the first open brace token...
        if token.value is '{':
            depth+=1
            collect_mode = True

    return extracted_body


def collect_method_tokens (index, collected_start_positions, java_tokenlist ):
    collect_method_tokens = False
    collected_method_tokens = []
    
    for token in java_tokenlist:
        if token.position is collected_start_positions[index]:
            collect_method_tokens = True
        if index+1 not in collected_start_positions:
            pass
        else:
            if token.position is collected_start_positions[index+1]:
                collect_method_tokens = False
            
        if collect_method_tokens is True:
            collected_method_tokens.append(token)
            
    return collected_method_tokens


def calculate_method_start_indexes_for_class( class_declaration ):
    collected_start_positions = []
    collected_method_names = []

    for j in range(len(class_declaration.methods)):
        # print("-- Methodname --")
        # print ( compilation_unit_ast.types[i].methods[j].name )
        # print("-- position of method --")
        # print (compilation_unit_ast.types[i].methods[j].position )
        # print (compilation_unit_ast.types[i].methods[j].modifiers)
        collected_start_positions.append(class_declaration.methods[j].position)
        collected_method_names.append(class_declaration.methods[j].name)
        # print("-- Body of method --")
        # print ( compilation_unit_ast.types[i].methods[j].body )

    return collected_start_positions, collected_method_names


# TODO: optimize this: because we will work on 2.1 million files, that must be fast
def extract_method( method_index , collected_start_positions, java_tokenlist):
    # ATTN: the start positions are off by the modifiers, ans start at the type signature.
    # TODO: should be optimized into one method, since it is basically collecting a longer
    #       list with "collect_method_teokens and then reducing it to a shorter version with 
    #       "extract_method_body"
    # rework token, extraction
    return extract_method_body ( collect_method_tokens( method_index, collected_start_positions, java_tokenlist ) ) 


# Will extract the methods of a class
def extract_methods_from_class( class_declaration, java_tokenlist ):
    extracted_methods = []
    
    collected_start_positions, collected_method_names = calculate_method_start_indexes_for_class(class_declaration)
    
    for index in range (len(collected_start_positions)):
        method_body = extract_method( index, collected_start_positions, java_tokenlist)
        method_dict_entry = {'method_body':method_body , 'method_name':collected_method_names[index], 'class_name': class_declaration.name }
        
        extracted_methods.append(method_dict_entry)
    
    return extracted_methods


def extract_allmethods_from_compilation_unit(compilation_unit_ast, java_tokenlist):
    all_methods = []
     
    for class_declaration in  compilation_unit_ast.types:
        extracted_methods = extract_methods_from_class(class_declaration, java_tokenlist )
        all_methods.extend(extracted_methods)
    
    return all_methods


def extract_classes_from_compilation_unit(compilation_unit_ast):
    classes = []

    for _,node in ast.walk_tree(compilation_unit_ast):
        if isinstance(node, ClassDeclaration):
            classes.append(node)
        
    [ print(clazz.name) for clazz in classes ]
    print (classes)
    return classes


def runTokenizerForFile(filename):
    with open(filename,"rb") as current_source_file:
        all_lines_as_string = map(lambda line: line.decode('utf-8'), current_source_file.readlines()[0:])
        current_source_code = "".join(all_lines_as_string) 
        return list(tokenizer.tokenize(current_source_code, ignore_errors=False))
    

def process_source_file(dataset_directory, source_file_path, encoder, dataset):
    # derive the full source file path
    full_source_file_path = os.path.join( dataset_directory, source_file_path);
    
    # Work on the source file
    java_tokenlist = runTokenizerForFile(full_source_file_path)
    parsed_compilation_unit = parser.parse(java_tokenlist)
    
    # collect file names, line numbers, method names, class names etc  
    all_methods_per_source = extract_allmethods_from_compilation_unit(parsed_compilation_unit, java_tokenlist)
    
    for single_method in all_methods_per_source:
        try:
            method_name = single_method['method_name']
            method_class_name = single_method['class_name']
            method_body = single_method['method_body']
            
            # encode body code and methodnames using the bpe-vocabulary
            bpe_encoded_methodname = encoder.encode( [ method_name ] )
            bpe_encoded_methodbody = encoder.encode([x.value for x in method_body])
            
            # do some calculations on the tokens and on the java code, so selection of smaller datasets is possible
            bpe_encoded_method_name_length = len(bpe_encoded_methodname)
            bpe_encoded_method_body_length = len(bpe_encoded_methodbody)
            
            # save this into dataset
            method_data = { 
                "source_file_path": source_file_path,
                "method_class_name": method_class_name,
                "method_name": method_name,
                "encoded_method_name_length": bpe_encoded_method_name_length,
                "encoded_method_name": bpe_encoded_methodname,
                "encoded_method_body_length": bpe_encoded_method_body_length,
                "encoded_method_body": bpe_encoded_methodbody,
                "method_body": method_body 
                }
            dataset.add_method_data( method_data )
        except:
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
        process_source_file('', current_source_filename, encoder, method_dataset)
    
    time_after_encoding = datetime.datetime.now()
    
    # print some statistics
    print( "===[ The End ]===")
    print( "time at start: " + str(time_at_start))
    print( "time after walking files: " + str(time_after_walkingfiles))
    print( "time when ready_encoding: " + str(time_after_encoding))


def doWork():
    model = BPEModel("16K-full", "../bpe/")
    model.load_hparams()
    
    # dataset_directory = 'D:\\Downloads\\Big-Code-full\\'
    dataset_directory = model.get_data_source_path()
    
    # only one class in compilation unit
    # some_source_filename = 'java_projects\\Algorithms\\src\\org\\rekdev\\trees\\BinaryTreeNode.java'
    
    # has multiple classes parallel in one compilation unit
    some_source_filename = 'java_projects\\CSSMin\\CSSMin.java'
    
    # nested classes
    # some_source_filename = 'java_projects\\cvs-plugin\\\src\\\main\\\java\\\hudson\\\scm\\CVSChangeLogSet.java'

    # inner and/or anonymous classes
    # TODO: anonymous innter classes won't be recognized as ClassDeclaration / ClassCreator kann im Body auch methodendeklarationen enthalten
    # some_source_filename = 'java_projects\\emf\\plugins\\org.eclipse.emf.codegen\\src\\org\\eclipse\\emf\\codegen\\CodeGen.java'
    
    model_vocabulary = model.load_tokens()
    model_bpe_data = model.load_bpe_pairs()
    
    encoder = SimpleBPEEncoder(model_vocabulary, model_bpe_data)
    
    method_dataset = MethodDataset()
    method_dataset.prepareNewDataset(dataset_directory)
    
    # TODO: and now crawl the directory and process each file...
    process_all_source_files(dataset_directory, encoder, method_dataset)
    
    # process_source_file(dataset_directory, some_source_filename, encoder, method_dataset)
    
    method_dataset.finish()
    pass


# TODO: the following things are part of the exploration of the resulting dataset        
# TODO: find duplicate methodnames, rank them, maybe cleanup dataset
# TODO: find bad methodnames
# TODO: build learning pairs for bad and good namings -- challenge number 5
if __name__ == '__main__':
    doWork()