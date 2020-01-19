'''
Created on 17.01.2020

* Prepare Methodname Dataset

@author: JohnDoe
'''


from com.github.c2nes.javalang import tokenizer, parser

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


def extract_method( method_index , collected_start_positions, java_tokenlist):
    # ATTN: the start positions are off by the modifiers, ans start at the type signature.
    # TODO: should be optimized into one method, since it is basically collecting a longer
    #       list with "collect_method_teokens and then reducing it to a shorter version with 
    #       "extract_method_body"
    return extract_method_body ( collect_method_tokens( method_index, collected_start_positions, java_tokenlist ) ) 

# Will extract the methods of a class
def extract_methods_from_class( class_declaration, java_tokenlist ):
    extracted_methods = []
    
    collected_start_positions, collected_method_names = calculate_method_start_indexes_for_class(class_declaration)
    
    for index in range (len(collected_start_positions)):
        method_for_index = extract_method( index, collected_start_positions, java_tokenlist)
        method_dict_entry = {'method_body':method_for_index , 'method_name':collected_method_names[index]}
        
        extracted_methods.append(method_dict_entry)
    
    return extracted_methods


def extract_allmethods_from_compilation_unit(compilation_unit_ast, java_tokenlist):
    
    # class can be the only one in a compilation unit
    # class can be in a class inside of a compilation unit
    # class can be in a method inside of a compilation unit
    # walk the tree and calculate the start positions of these classes / return the classes, and then do the rest on them
    
    # I guess it would be better to use a walker, which is able to find each class_declaration, instead of iterating over the class only 
    for i in range(len(compilation_unit_ast.types)):
        class_declaration = compilation_unit_ast.types[i]
        extracted_methods = extract_methods_from_class(class_declaration, java_tokenlist )

        for single_method in extracted_methods:
            print("==["+single_method['method_name']+"]==")
            print(tokenizer.reformat_tokens(single_method['method_body']))
    pass

def doWork():
    print("Hello world!")
    pass

if __name__ == '__main__':
    doWork()