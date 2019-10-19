'''
Created on 19.10.2019

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
from _collections import OrderedDict

class TokenStatistics(object):
    def __init__(self):
        self.__statistics = {}
    
    def update(self, dictionary):
        for key, count in dictionary.items():
            if key not in self.__statistics:
                self.__statistics[key] = count
            else:
                self.__statistics[key] += count
        pass
    
    def get(self):
        return self.__statistics
    
    def load(self, filepath):
        with open(filepath,'r') as wordfile:
            self.__statistics = json.load(wordfile)

        return self.__statistics
    
    def _sort_tokens_by_occurence_asc(self, token_map):
        return OrderedDict(sorted(token_map.items(), key=lambda item:item[1]))
    
    def save(self, filepath, dictionary=None):
        if dictionary is None:
            dictionary = self.__statistics
        with open(filepath, 'w') as global_count_file:
            json.dump(self._sort_tokens_by_occurence_asc(dictionary), global_count_file)
