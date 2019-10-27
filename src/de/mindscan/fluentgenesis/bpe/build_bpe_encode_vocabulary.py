'''
Created on 04.08.2019

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
import regex as re

from com.github.c2nes.javalang import tokenizer
from _collections import OrderedDict

from de.mindscan.fluentgenesis.bpe.token_statistics import TokenStatistics
from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel

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

def runTokenizerForFile(filename):
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

def get_occurence_frequency2(sorted_token_list):
    ngram_frequency = {}
    for token_as_tuple, count in sorted_token_list.items():
        token_pairs = get_lexeme_pairs(token_as_tuple)
        for pair in token_pairs:
            if pair not in ngram_frequency:
                ngram_frequency[pair] = 0;
            ngram_frequency[pair]+=count
    return ngram_frequency

emitted_tokens = {}
current_emitted_token_index = 0
emitted_bpe = {}
current_emitted_bpe_index=0;

def emit_token(key):
    global emitted_tokens
    global current_emitted_token_index
    if key not in emitted_tokens:
        current_emitted_token_index += 1
        emitted_tokens[key] = current_emitted_token_index

def get_emitted_token_dict():
    global emitted_tokens
    return emitted_tokens

def emit_probability(mp_token_pair, count):
    global emitted_bpe
    global current_emitted_bpe_index
    try:
        emitted_bpe[current_emitted_bpe_index]= {str(mp_token_pair):count}
    except:
        try:
            emitted_bpe[current_emitted_bpe_index]= {str(mp_token_pair).encode('utf_8'):count}
        except:
            print ("could not emit good pair... encoding might be shit now...")
            
    current_emitted_bpe_index+=1

def get_emitted_bpe_list():
    global emitted_bpe
    return emitted_bpe

def emit_most_probable_lexeme(mp_token_pair, count_of_most_probable_token):
    try:
        emit_token("".join(mp_token_pair))
        emit_probability(mp_token_pair, count_of_most_probable_token)
        try:
            print("emit rank - most frequent element: " + str(mp_token_pair).encode("utf-8") + " occurences...("+ str(count_of_most_probable_token) +")")
        except:
            try:
                print("emit rank - most frequent element: " + str(mp_token_pair) + " occurences...("+ str(count_of_most_probable_token) +")")
            except:
                print("cannot report token... but it got emitted.")
    except:
        print("could not emit token properly.")
        
        
def emit_complete_tokens(current_token_map):
    for key in current_token_map.keys():
        if len(key) is 1:
            if type(key) is list:
                emit_token(key[0])
            else:
                if type(key) is tuple:
                    emit_token(key[0])
                else:
                    emit_token(key)
    pass


def emit_unknown_partial_lexemes(current_token_map):
    for key, _ in current_token_map.items():
        for token in key:
            # token might already be present because of encoding in progress, but other components might be still unknown.
            emit_token(token)
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
        
        new_key = build_replacement_key_for(token, first_mptl, next_mptl, joined)
        
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
    
    current_iterator = iter(sorted_current_lexeme_frequencies)
    
    first_element = next(current_iterator)
    first_occurences = current_token_frequencies[first_element]
    
    next_element = next(current_iterator)
    next_occurences = current_token_frequencies[next_element]
    
    # first is max.
    if(first_occurences > next_occurences):
        return first_element
    
    # at least two elements have the same count, we should collect them and rank them.
    same_probability = []
    same_probability.append(first_element)
    same_probability.append(next_element)

    try:    
        while True:
            next_element = next(current_iterator)
            next_occurences = current_token_frequencies[next_element]
            
            if first_occurences == next_occurences:
                same_probability.append(next_element)
            else:
                break;
    except:
        # TOOD: will have to investigate that... especially
        # case 1, next_occurence is 1 
        pass
    
    #
    #try:
    #    print("We have more than one element with this occurence: "+ str(same_probability).encode("utf-8") + " occurence: "+ str(first_occurences).encode("utf-8"))
    #except:
    #    pass
    
    # this is better than before but, it is still not the perfect strategy, to collect good words.  
    # maybe we have to mix it with real wor(l)d statistics? or cheat on othe bpe-data, to make a better choice?
    # but i guess, 14 GB of sourcecode can solve the statistics problem.
    # Maybe we should not count "words" if they are too long... see (get_occurence_frequency2)
    # Because in the end we still compose to big words... and start clogging up the dictionary with technical jargon...
    shortest_element = min(same_probability, key=(lambda pair: len(pair[0])+len(pair[1])))
    
    return shortest_element

def find_word_containing( pair, current_token_map ):
    left, right = pair
    for element, _ in current_token_map.items():
        if left not in element:
            continue
        if right not in element:
            continue
        
        i=0;
        while i<len(element):
            try :
                i=element.index(left,i)
            except:
                break;
            
            if i+1 < len(element) and element[i+1]==right:
                return element
            else:
                i+=1
    pass


def build_dictionary(hparams, token_map):
    # emit all one element tokens
    # create a copy of the  
    current_token_map=rebuild_token_map(token_map)
    #print (str(current_token_map).encode("utf-8"))
    
    print("the whole dictionary has now length : " + str(len(current_token_map)))
    
    emit_complete_tokens(current_token_map)
    current_token_map = remove_completed_tokens(current_token_map)
    # print (str(current_token_map).encode("utf-8"))
    
    print("the whole dictionary has now length : " + str(len(current_token_map)))
    
    ## FOR - number of iterations / or there is no most probable lexeme anymore (count of lexems is one)
    for i in range(hparams['tokens_to_emit']):
        print("------------------------------------")
        print("Round: "+str(i))
        
        # TODO: nur jede n-te runde berechnen, eigentlich so lange, 
        # wie das ende eines Tokens nicht der start eines frueheren anderen Tokens ist
        # und der start eines Tokens nicht das ende eines frueheren anderen Tokens ist
        # so lange stimmt die Reihenfolge naemlich...
        # nur dann muessen die frequenzen neu berechnet werden.
        # andernfalls brauchen nur die ersetzungen erfolgen.
        current_token_frequencies = get_occurence_frequency2(current_token_map)
            
        mp_token_pair = select_best_bpe_match(current_token_frequencies)
        
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
        
        if i%10 == 0:
            print("the whole dictionary has now length : " + str(len(current_token_map)))
        # current_token_map = emit_tokens(current_token_map)
    
    # break if to many tokens emitted
    
    # flush all remaining single tokens / flush all remaining tokens not in the tokenlist.
    emit_unknown_partial_lexemes(current_token_map)
    pass


# this should be a producer, which is always retrieves the next file.
def walkFiles(path):
    filenames = []
    for root, _, files in os.walk(path):
        for file_ in files:
            filenames.append(os.path.realpath(os.path.join(root, file_)))
    return filenames




# TODO: regex-split on heavy strings, if split, then it will produce more convincing words and tokens.
#       see often useless concatenations with quotations, comma, period and undesired spaces as well concatenations of strings and numbers, when not needed.  
def split_rare_dictionary_items(hparams, _theGlobalTokenMap):
    splitDictionaryItems={}
    
    # this very useful regex pattern comes from "openai/gpt-2" implementation
    # https://github.com/openai/gpt-2 also MIT-License
    # https://github.com/openai/gpt-2/blob/master/LICENSE
    thepattern = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
    
    to_remove = []
    numberOfItems = 0
    for token, count in _theGlobalTokenMap.items():
        if count < hparams['split_if_occurence_less_than']:
            to_remove.append(token)
            try:
                numberOfItems += 1
                # print("#" + str(numberOfItems)+" count "+ str(count)+" length: " + str(len(token))+" value: " + str(token))
                for textToken in re.findall(thepattern, token):
                    #print("--> would be split into: " + str(textToken))
                    if textToken in splitDictionaryItems:
                        splitDictionaryItems[textToken] += count
                    else:
                        splitDictionaryItems[textToken] = count
            
            except:
                print()
    
    for token in to_remove:
        _theGlobalTokenMap.pop(token)
        
    return splitDictionaryItems


def run_me(model):
    hparams = model.read_hparams()
    
    time_at_start = datetime.datetime.now()
    print( "time at start: " + str(time_at_start))
    time_after_walkingfiles = None
    time_after_aggregating_statistics = None
    time_after_splitting_leastFrequentWords = None

    statistics = TokenStatistics();

    if os.path.isfile(model.get_global_tokenstatistics_path()) is False:
        
        filenames = walkFiles(hparams['path'])
        time_after_walkingfiles = datetime.datetime.now()
        print( "time after walking files: " + str(time_after_walkingfiles))
        
        for filename in filenames:
            try:
                print("tokenizing :'"+filename+"'")
                
                # all tokens in serialized form for this file
                tokens_for_file = runTokenizerForFile(filename)
                
                # all tokens aggregated
                aggregated_tokenoccurence_for_file = calculateTokenOccurence(tokens_for_file)
                
                # update globally aggregated tokens
                statistics.update(aggregated_tokenoccurence_for_file)
            except:
                try:
                    print ("Not considered this one..." + filename)
                except:
                    print ("filename is strange...")
        
        _theGlobalTokenMap=statistics.get()
        
        time_after_aggregating_statistics = datetime.datetime.now()
        print( "time after aggregating words: " + str(time_after_aggregating_statistics))
    
        newDict = split_rare_dictionary_items(hparams, _theGlobalTokenMap)
        statistics.update(newDict)
    
        _theGlobalTokenMap=statistics.get()
            
        time_after_splitting_leastFrequentWords = datetime.datetime.now()
        print( "time after splitting least frequent words: " + str(time_after_splitting_leastFrequentWords))
        
        print("number of items in new dictionary: " + str(len(newDict)))
    
        statistics.save(model.get_global_tokenstatistics_path(), _theGlobalTokenMap)
    else:
        _theGlobalTokenMap = statistics.load(model.get_global_tokenstatistics_path())
    
    print("number of items merged dictionary: " + str(len(_theGlobalTokenMap)))
    
    build_dictionary(hparams,_theGlobalTokenMap)
    
    time_after_buildingDict = datetime.datetime.now()
    print( "time after building dictionary: " + str(time_after_buildingDict))

    model.save_bpe_pairs(get_emitted_bpe_list())
    model.save_tokens(emitted_tokens)
    
    print( "===[ The End ]===")
    print( "time at start: " + str(time_at_start))
    if time_after_walkingfiles is not None: 
        print( "time after walking files: " + str(time_after_walkingfiles))
    if time_after_aggregating_statistics is not None:
        print( "time after aggregating words: " + str(time_after_aggregating_statistics))
    if time_after_splitting_leastFrequentWords is not None:
        print( "time after splitting least frequent words: " + str(time_after_splitting_leastFrequentWords))
    print( "time after building dictionary: " + str(time_after_buildingDict))
    
    pass
    

if __name__ == '__main__':
    # "1K-datapoint", "10K-excerpt", "16K-excerpt", "50K-full", "100K-full"
    model = BPEModel("1K-datapoint") 
    
    run_me(model)
