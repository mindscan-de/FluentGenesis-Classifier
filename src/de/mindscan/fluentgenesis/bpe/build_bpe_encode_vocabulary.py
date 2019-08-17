'''
Created on 04.08.2019

@author: Maxim Gansert, Mindscan
'''
from com.github.c2nes.javalang import tokenizer
from _collections import OrderedDict

def get_lexeme_pairs(word):
    lexeme_pairs = []
    prev_lexeme = word[0]
    for current_lexeme in word[1:]:
        lexeme_pairs.append((prev_lexeme, current_lexeme))
        prev_lexeme = current_lexeme
    return lexeme_pairs


# Step 1 - Build global token statistics
# --------------------------------------
# Iterate through all files,
# for each file 
## Tokenize each file
## collect statistics for each token and count each token
## update global statistics
# save global statistics

def runTokenizer(filename):
    with open(filename,"rb") as current_source_file:
        all_lines_as_string = map(lambda line: line.decode('utf-8'), current_source_file.readlines()[0:])
        current_source_code = "".join(all_lines_as_string) 
        return list(tokenizer.tokenize(current_source_code, ignore_errors=False))

def calculateTokenOccurence( tokens ):
    result = {}
    for token in tokens:
        token_value = token.value
        if not token_value in result:
            result[token_value]=0
        result[token_value]+=1
    return result

## TODO: save tokenmap
## TODO: load tokenmap

# Step 2 - Build compression dictionary / compress dictionary save and emit new codes and stats
# -------------------------------------
# load global statistics
# calculate the statistics for all bytepairs
# process all tokens with length 1 order them by occurence
# emit token to index, and absolute count (int32), and relative count (float32?)
# keep them in index

# take current dictionary
#
# calculate build-pairs for each word in dictionary - calculate global statistics for each pair
# select most common pair
# emit pair to index,
# replace all occurences of this pair in the whole dictionary and join them

def sort_by_lexeme_occurence(token_map):
    return OrderedDict(sorted(token_map.items(), key=lambda item:item[1], reverse=True ))


def get_occurence_frequency(sorted_token_list):
    ngram_frequency = {}
    for token, count in sorted_token_list.items():
        #token_as_tuple = tuple(token)
        token_as_tuple = token
        token_pairs = get_lexeme_pairs(token_as_tuple)
        for pair in token_pairs:
            if pair not in ngram_frequency:
                ngram_frequency[pair] = 0;
            ngram_frequency[pair]+=count
    return ngram_frequency

def get_occurence_frequency2(sorted_token_list):
    ngram_frequency = {}
    for token_as_tuple, count in sorted_token_list.items():
        token_pairs = get_lexeme_pairs(token_as_tuple)
        for pair in token_pairs:
            if pair not in ngram_frequency:
                ngram_frequency[pair] = 0;
            ngram_frequency[pair]+=count
    return ngram_frequency



def emit_most_probable_lexeme(mp_token_pair, count_of_most_probable_token):
    print("emit rank - most frequent element: " + str(mp_token_pair) + " occurences...("+ str(count_of_most_probable_token) +")")
    print("emit also as token.")


def emit_complete_tokens(current_token_map):
    for key in current_token_map.keys():
        if len(key) is 1:
            print("emit token - because it is complete now: " + key[0])
    pass


def remove_completed_tokens(current_token_map):
    keys_to_remove = []
    for key in current_token_map.keys():
        if len(key) is 1:
            keys_to_remove.append(key)
             
    if len(keys_to_remove) >0:
        for key in keys_to_remove:
            del current_token_map[key]
            
    return current_token_map


def rebuild_token_map(token_map):
    result = dict()
    for key, value in token_map.items():
        token_as_tuple = tuple(key)
        result[token_as_tuple] = value
    
    return result


def calculate_replacement_key_for(token, first_mptl, next_mptl, joined):
    replacement_key=[]
    
    i=0
    while i<len(token):
        # copy all items to replacement_key before first_mptl
        try:
            j=token.index(first_mptl,i)
            replacement_key.extend(token[i:j])
            i=j
        except:
            replacement_key.extend(token[i:])
            break;
        
        if token[i] == first_mptl and i<len(token)-1 and token[i+1] == next_mptl:
            # if next is next_mptl -> add joined to list
            replacement_key.append(joined)
            i+=2
        else:
            # if next is not next_mptl -> only the first_mptl 
            replacement_key.append(token[i])
            i+=1
        # then copy more, till ready
    
    print(str(token) +" -> " + str(replacement_key) + " because: " + str(joined))    
    return tuple(replacement_key)


def replace_most_probable_lexemes(mp_token_pair, current_token_map):
    joined = "".join(mp_token_pair)
    removal_list = []
    additions_list = {}
    
    first_mptl, next_mptl = mp_token_pair
    
    # update all lexemes/tokens in current token map. 
    for token, count in current_token_map.items():
        # is the tokenpair  part of the current token?
        # if no just continue with next element
        if first_mptl not in token:
            continue
        if next_mptl not in token:
            continue
        
        # more expensive implementation of substitution
        # replace each occurence of the mp_token_pair with the joined key
        new_key = calculate_replacement_key_for(token, first_mptl, next_mptl, joined)
        
        # if still the same, we do nothing        
        if new_key == token :
            continue
        
        # add to removal list
        removal_list.append(token)
        # add new element (joined) to add list
        additions_list[new_key] = count
        
    for remove_key in removal_list:
        current_token_map.pop(remove_key)

    for addition_key, count in additions_list.items():
        current_token_map[addition_key] = count
        
    return current_token_map


#
# Problem is, These elements need ranking... we to prefer smaller joins to bigger joins,
# otherwise we are adding one letter next to the word and the dictionary gets polluted 
# part by part by the most frequent word, instead of the buildingblocks (smaller lexemes) of the words
# both lexemes should be of nearly equal length as well, so that we do not end up adding one letter at 
# a time, but we still want that behavior, but maybe later on... when working on the dictionary.
# 
# we should rank if multiple candidates are found  
#
def select_best_bpe_match(current_token_frequencies):
    sorted_current_lexeme_frequencies = sort_by_lexeme_occurence(current_token_frequencies)
    return next(iter(sorted_current_lexeme_frequencies))



def build_dictionary(token_map):
    # emit all one element tokens
    # create a copy of the  
    current_token_map=rebuild_token_map(token_map)
    print (current_token_map)
    
    emit_complete_tokens(current_token_map)
    current_token_map = remove_completed_tokens(current_token_map)
    print (current_token_map)
    
    ## FOR - number of iterations / or there is no most probable lexeme anymore (count of lexems is one)
    for i in range(80):
        print("------------------------------------")
        print("Round: "+str(i))
        print("------------------------------------")
        
        # find the most fequent / most probable pair
        current_token_frequencies = get_occurence_frequency2(current_token_map)
        mp_token_pair = select_best_bpe_match(current_token_frequencies)
        
        ## ONLY WITH the for - loop
        if current_token_frequencies[mp_token_pair] < 2:
            # we are ready, we do not have any duplicates
            break
        
        # emit first_token_pair
        emit_most_probable_lexeme(mp_token_pair, current_token_frequencies[mp_token_pair])
        
        # replace the first tokenpair on whole token_map
        current_token_map = replace_most_probable_lexemes(mp_token_pair, current_token_map ) 
        
        # emit all complete tokens
        emit_complete_tokens(current_token_map)
        current_token_map = remove_completed_tokens(current_token_map)
        # current_token_map = emit_tokens(current_token_map)
    
    # break if to many tokens emitted
    
    # flush all remaining single tokens / flush all remaining tokens not in the tokenlist.
    # flush all other statistics
   
    # collect all remaining lexemes in the remaining map, with length 1 and write them into the tokenlist

if __name__ == '__main__':
    tokens = runTokenizer("D:\\Projects\\SinglePageApplication\\Angular\\FluentGenesis-Classifier\\ipynb\\java-example\\1datapoint\\gen\\com\\onedatapoint\\R.java")
    print(tokens)
    
    _token_map = calculateTokenOccurence(tokens)
    #print(token_map)
    
    #frequency2 = get_occurence_frequency(token_map)
    #print(sort_by_lexeme_occurence(frequency2))
    
    build_dictionary(_token_map)
    
    pass