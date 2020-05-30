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

from com.github.c2nes.javalang import tokenizer 

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


# This collection of the method has O(n^2) compexity - this should be corrected, especially because there are many tokens.
# When i was implementing this i just wanted to have that working, i didn't care about the runtime, but having a quadratic runtime
# on approximately 2 Billion tokens is no laughing matter.   
# bt methods can include other classes and methods, so it is not just a linear thing going on, but for most of the cases it is fine
# but the sourcecode processed teaches otherwise.
def collect_method_tokens (index, collected_start_positions, java_tokenlist ):
    collect_method_tokens_enabled = False
    
    collect_body_mode = False
    extracted_body = []
    depth = 0    
    
    for token in java_tokenlist:
        if token.position is collected_start_positions[index]:
            collect_method_tokens_enabled = True
            
        if collect_method_tokens_enabled is True:
            # don't collect the last closing brace token...
            if token.value is '}':
                depth-=1
                if depth is 0:
                    collect_body_mode=False
                    # break this loop, since all is done / we have more closing braces than opening braces.
                    break
            
            if collect_body_mode:
                extracted_body.append(token)
    
            # don't collect the first open brace token... / append is done before.
            if token.value is '{':
                depth+=1
                collect_body_mode = True
            
    return extracted_body


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


def extract_method( method_index , collected_start_positions, java_tokenlist):
    return collect_method_tokens( method_index, collected_start_positions, java_tokenlist ) 


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



def tokenize_file(source_code_filename):
    with open(source_code_filename,"rb") as current_source_file:
        all_lines = map(lambda line: line.decode('utf-8'), current_source_file.readlines()[0:])
        all_lines_joined = "".join(all_lines)
        return list(tokenizer.tokenize(all_lines_joined, ignore_errors=False))
