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

from functools import lru_cache

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


def find_first_repetition_start(frequencies):
    last_frequency = -1
    for i in range(0,len(frequencies)):
        if last_frequency == frequencies[i]:
            # if current element is as frequent as last, repetition started at last index
            return i - 1
        last_frequency = frequencies[i]
    return len(frequencies)


def find_first_interference_index(candidates):
    last_word = set()
    first_word = set()
    
    for i in range(0, len(candidates)):
        if candidates[i][0] in last_word:
            return i
        if candidates[i][1] in first_word:
            return i
        
        first_word.add( candidates[i][0])
        last_word.add( candidates[i][1])
        
    return len(candidates)

#
# This algorithm works like this it compares frequencies of the words, we are creating either runlength of token-pairs with same frequency or with decreasing frequencies
# runlength with same frequencies are ordered by shorter length first to longer length
# runlength with decreasing frequencies are stopped when a run of same frequencies is detected
# 
# Both runlength may require recalculations of the statistics, if a substitution creates an interference in the statistics, 
# but it they do not interfere, we can avoid the recalculation of the statistics, 
# and a collection of noninterfering bpe matches is returned
#
# That strategy helps to reduce the amount of recalculations of the statistics
#
def collect_best_bpe_matches2(current_token_frequencies):
    sorted_current_lexeme_frequencies = sort_by_lexeme_occurence(current_token_frequencies)
    
    # read first 128 most probable token pair frequencies
    most_frequent_items = list(sorted_current_lexeme_frequencies.items())[:128]
    
    # read first two and compare frequenciesand derive how to proceed
    # first_element = most_frequent_items[0][0]
    first_element_occurence = most_frequent_items[0][1]
    # second_element = most_frequent_items[1][0]
    second_element_occurence = most_frequent_items[1][1]
    
    if(first_element_occurence == second_element_occurence):
        # if equal, select all pairs with that frequency
        filtered_first_same_frequent_items = [ item[0] for item in most_frequent_items if item[1] == first_element_occurence ]
        # sort them by length of concatenation
        candidates = list(sorted(filtered_first_same_frequent_items, key=(lambda pair: len(pair[0])+len(pair[1])) ))
        # TODO: Improvement we can append them by a run until next repetitions, this should be cool too
        #       with larger corpora, we get a run of a few elements with same occurences, followed by more with decreasing occurences
        #       we handle same occurences special, because we order them and the ordering is basically done here, so now we can append
        #       more elements to the candidates
        #       that will save a lot of computation time....  
        #       because in the last 40% of the processing of the corpus it slows down very noticably...
        #       even then appending it would also be very valueable..
    else:
        # if not equal, select all pairs until two occur, which are equal
        frequencies = [ item[1] for item in most_frequent_items ]
        first_rep = find_first_repetition_start(frequencies)
        
        if first_rep==-1: 
            first_rep = 1;
            
        candidates = [ item[0] for item in most_frequent_items[:first_rep] ]
 
    # no interferences when only one candidate present
    if len(candidates) == 1 :
        return candidates

    # find the interference    
    first_interference_index = find_first_interference_index(candidates)
    
    # no interference found
    if first_interference_index == len(candidates):
        return candidates
    
    # reduce the list until the element occurs which requires updated statistics.
    non_interferencing_candidates = candidates[:first_interference_index]
    try:
        print( "Interference found " + str(non_interferencing_candidates) + " with "+ str(candidates[first_interference_index]))
    except:
        pass
    return non_interferencing_candidates


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

def emit_obvious_ascii_tokens(token_map):
    # range is 32 to 256-1
    for char in range(32, 256):
        emit_token(chr(char))
        
unsupported_vocab_ranges = [
        # Latin Extended
        (0x0100, 0x017F),  # Latin Extended-A
        (0x0180, 0x024F),  # Latin Extended-B
        (0x1E00, 0x1EFF),  # Latin Extended Additional
        (0x2C60, 0x2C7F),  # Latin Extended-C
        (0xA720, 0xA7FF),  # Latin Extended-D
        (0xAB30, 0xAB6F),  # Latin Extended-E
    
        # Diacritical
        (0x0300, 0x036F),  # Combining Diacritical Marks
        (0x1AB0, 0x1AFF),  # Combining Diacritical Marks Extended
        (0x1DC0, 0x1DFF),  # Combining Diacritical Marks Supplement
        (0x20D0, 0x20FF),  # Combining Diacritical Marks for Symbols
    
        # IPA & phonetic Extemsion
        (0x0250, 0x02AF),  # IPA Extensions
        (0x1D00, 0x1D7F),  # Phonetic Extensions
        (0x1D80, 0x1DBF),  # Phonetic Extensions Supplement
    
        # Spacing Modifier Letters
        (0x02B0, 0x02FF),  # Spacing Modifier Letters
    
        # Greek Coptic
        (0x0370, 0x03FF),  # Greek and coptic
        (0x1F00, 0x1FFF),  # Greek Extended
        (0x2C80, 0x2CFF),  # Coptic
    
        # Cyrillic
        (0x0400, 0x04FF),  # Cyrillic)
        (0x0500, 0x052F),  # Cyrillic Supplement
        (0x2DE0, 0x2DFF),  # Cyrillic Extended-A
        (0xA640, 0xA69F),  # Cyrillic Extended-B
        (0x1C80, 0x1C8F),  # Cyrillic Extended-C
    
        # Armenian
        (0x0530, 0x058F),  # Armenian 
    
        # Hebrew
        (0x0590, 0x05FF),  # Hebrew
    
        # Arabic
        (0x0600, 0x06FF),  # Arabic
        (0x0750, 0x077F),  # Arabic Supplement
        (0x08A0, 0x08FF),  # Arabic Extended-A
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms B
    
        # Syriac
        (0x0700, 0x074F),  # Syriac
        (0x0860, 0x086F),  # Syriac Supplement
    
        # Thaana
        (0x0780, 0x07BF),  # Thaana
    
        # NKo
        (0x07C0, 0x07FF),  # NKo
    
        # Samritan
        (0x0800, 0x083F),  # Samaritan
    
        # Mandaic
        (0x0840, 0x085F),  # Mandaic
    
        # Invalid range
        (0x0870, 0x089F),  # Invalid range

        # Indian Subkontinent Languages
        (0x0900, 0x097F),  # Devanagari
        (0xA8E0, 0xA8FF),  # Devanagari Extended
         
        # (0x0980, 0x09FF), # Bengali
        # ...
        (0x0900, 0x0DFF),  # India - covers multiple languages
        (0xA830, 0xA83F),  # Common Indic Number Forms


        (0x0E00, 0x0E7F),  # Thai
        (0x0E80, 0x0EFF),  # Lao
    
        (0x0F00, 0x0FFF),  # Tibetan
    
        # Myanmar
        (0x1000, 0x109F),  # Myanmar
        (0xAA60, 0xAA7F),  # Myanmar Extended-A
        (0xA9E0, 0xA9FF),  # Myanmar Extended-B
    
        # Georgian
        (0x10A0, 0x10FF),  # Georgian
        (0x2D00, 0x2D2F),  # Georgian Supplement
        (0x1C90, 0x1CBF),  # Georgian Extended
    
        # Korean
        (0x1100, 0x11FF),  # Hangul Jamo    
        (0x3130, 0x318F),  # Hangul Compatibility Jamo    
        (0xAC00, 0xD7AF),  # Hangul Syllables
        (0xA960, 0xA97F),  # Hangul Jamo Extended-A
        (0xD7B0, 0xD7FF),  # Hangul Jamo Extended B
    
        # Ethiopic
        (0x1200, 0x139f), # Ethiopic, Ethopic Supplement
        (0xAB00, 0xAB2F), # Ethiopic Extended-A
        (0x2D80, 0x2DDF), # Ethiopic Extended

        # Cherokee
        (0x13A0, 0x13FF),  # Cherokee
        (0xAB70, 0xABBF),  # Cherokee Supplement
    
        # Canadian Aboriginal
        (0x1400, 0x167F),  # Unified Canadian Aboriginal Syllabics
        (0x18B0, 0x18FF),  # Unified Canadian Aboriginal Syllabics Extended
    
    
        (0x1680, 0x169F),  # Ogham
        (0x16A0, 0x16FF),  # Runic
        (0x1700, 0x171F),  # Tagalog
        (0x1720, 0x173F),  # Hanunoo
        (0x1740, 0x175F),  # Buhid
        (0x1760, 0x177F),  # Tagbanwa
        
        # Khmer
        (0x1780, 0x17FF),  # Khmer
        (0x19E0, 0x19FF),  # Khmer Symbols
    
        # Mongolian
        (0x1800, 0x18AF),  # Mongolian

        (0x1900, 0x194F),  # Limbu
        (0x1950, 0x197F),  # Tai Le
        (0x1980, 0x19DF),  # New Tai Lue
    
        (0x1A00, 0x1A1F),  # Buginese
        (0x1A20, 0x1AAF),  # Tai Tham
    
        (0x1B00, 0x1B7F),  # Balinese
    
        (0x1B80, 0x1BBF),  # Sundanese
        (0x1CC0, 0x1CCF),  # Sundanese Supplement
    
        (0x1BC0, 0x1BFF),  # Batak
    
        (0x1C00, 0x1C4F),  # Lepcha
        (0x1C50, 0x1C7F),  # Ol Chiki
        (0x1CD0, 0x1CFF),  # Vedic Extensions
    
        # Punctuation
        (0x2000, 0x206F),  # General Punctuation
        (0x2E00, 0x2E7F),  # Supplemental Punctuation
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        
        (0x2070, 0x209F),  # Superscripts and Subscripts
        (0x20A0, 0x20CF),  # Currency Symbols
    
    
        # Symbols
        (0x2100, 0x26ff), # Letterlike Symbols, ... Miscelaneous Symbols
        (0x2700, 0x27FF), # Dingbats & co
        (0x2800, 0x28FF), # Braille
        (0x2900, 0x2BFF), # Symbols Arrows math
    
        (0x2D30, 0x2D7F),  # Tifinagh
        
        (0x2f00, 0x2FFF),  # Kangxi radicals, Ideographic Description Characters
    

        # CJK
        (0x3000, 0xa4FF),
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
        (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
        (0x2E80, 0x2EFF),  # CJK Radicals Supplement
    

        #
        (0xA500, 0xA63F),  # Vai
        (0xA6A0, 0xA6FF),  # Bamum
        (0xA700, 0xA71F),  # Modifier Tone Letters
        (0xA800, 0xA82F),  # Syloti Nagri
        (0xA840, 0xA87F),  # Phags-pa
        (0xA880, 0xA8DF),  # Saurashtra
        (0xA900, 0xA92F),  # Kayah Li
        (0xA930, 0xA95F),  # Rejang
        (0xA980, 0xA9DF),  # Javanese
    
        (0xAA00, 0xAA5F),  # Cham
        (0xAA80, 0xAADF),  # Tai Viet
    
        (0xABC0, 0xABFF),  # Meetei Mayek
        (0xAAE0, 0xAAFF),  # Meetei Mayek Extensions

        # Private Area
        (0xE000,0xF8FF),  # Private Use Area
        (0xD800, 0xDB7F), # High Surrogates
        (0xDB80, 0xDBFF), # High Private Use Surrogates
        (0xDC00, 0xDFFF), # Low Surrogates
        # ???
        (0x2c00, 0x2c5f), # Glagolitic
        
    
        (0xFB00, 0xFB4F),  # Alphabetic Presentation Forms
        (0xFE00, 0xFE0F),  # Variation Selectors
        (0xFE10, 0xFE1F),  # Vertical Forms
        (0xFE20, 0xFE2F),  # Combining Half Marks
        (0xFE50, 0xFE6F),  # Small Form Variants
        
        (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
    
        # OLD and OLDER
        (0x010000, 0x10FFFF) # Basically everything what is not as important to be in first ~65000 Codes
    ]

@lru_cache(maxsize=None)
def is_unsupported_range(char):
    char = ord(char)
    for bottom, top in unsupported_vocab_ranges:
        if char >= bottom and char <= top:
            return True
    return False
        
def contains_unsupported_vocab(key):
    for c in key:
        if is_unsupported_range(c):
            return True
    return False
        
def remove_tokens_containing_unsupported_chars(current_token_map):
    keys_to_remove = []
    for key in current_token_map.keys():
        if contains_unsupported_vocab(key):
            keys_to_remove.append(key)
             
    if len(keys_to_remove) >0:
        for key in keys_to_remove:
            del current_token_map[key]
            
    return current_token_map

def remove_rare_tokens(current_token_map):
    keys_to_remove = []
    for key, count in current_token_map.items():
        if count < 6:
            keys_to_remove.append(key)
             
    if len(keys_to_remove) >0:
        for key in keys_to_remove:
            del current_token_map[key]
            
    return current_token_map

def build_dictionary_faster(hparams, token_map):
    current_token_map = rebuild_token_map(token_map)
    #print (str(current_token_map).encode("utf-8"))
    
    print("the whole dictionary has now length : " + str(len(current_token_map)))
    print("removing rare tokens")
    current_token_map = remove_rare_tokens(current_token_map)
    
    print("the whole dictionary has now length : " + str(len(current_token_map)))
    
    print("removing tokens containing unsupported characters")
    # remove asian tokens, because they cause the tokens to inflate too much, and I do not have enough training data for these "rare" tokens
    # the asian characters alone will clog up the entire available dictionary
    current_token_map = remove_tokens_containing_unsupported_chars(current_token_map)
    
    print("the whole dictionary has now length : " + str(len(current_token_map)))
    print("emitting ascii and complete tokens")

    # emit all (important) one element tokens
    emit_obvious_ascii_tokens(current_token_map)
    emit_complete_tokens(current_token_map)
    
    current_token_map = remove_completed_tokens(current_token_map)
    
    print("the whole dictionary has now length : " + str(len(current_token_map)))
    
    # print (str(current_token_map).encode("utf-8"))
    
    mp_token_pairs = []
    
    stats_calculated = 0
    ## FOR - number of iterations / or there is no most probable lexeme anymore (count of lexems is one)
    i=0
    while i < hparams['tokens_to_emit']:
        print("------------------------------------")
        print("Round: "+str(i))
        
        if len(mp_token_pairs) == 0:
            stats_calculated += 1
            current_token_frequencies = get_occurence_frequency2(current_token_map)
            mp_token_pairs = collect_best_bpe_matches2(current_token_frequencies)
            
        mp_token_pair = mp_token_pairs[0]
        del mp_token_pairs[0]
        
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
        
        i = i+1
    
    # break if to many tokens emitted
    
    # flush all remaining single tokens / flush all remaining tokens not in the tokenlist.
    emit_unknown_partial_lexemes(current_token_map)
    
    print("Statistics were calculated %d times"%stats_calculated)
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
    hparams = model.load_hparams()
    
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
            # skip non java files
            if not filename.endswith(".java"):
                continue
            
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
    
    build_dictionary_faster(hparams,_theGlobalTokenMap)
    
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
    # model = BPEModel("1K-datapoint") 
    model = BPEModel("16K-full")
    # model = BPEModel("16K-excerpt")
    model.load_hparams()
    
    run_me(model)
