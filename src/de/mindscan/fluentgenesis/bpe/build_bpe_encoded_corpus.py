'''
Created on 02.11.2019

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

from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel

# walk the corpus, load each file
# tokenize and save result into json-file
# all the files needs to be recalculated if encoding table is renewed

# the json file can later be used to calculate the embeddings and also 
# be the source of truth for BERT and other training methods, in the 
# transformer model.

# this should be a producer, which is always retrieves the next file.
def walkFiles(path):
    filenames = []
    for root, _, files in os.walk(path):
        for file_ in files:
            filenames.append(os.path.realpath(os.path.join(root, file_)))
    return filenames



# bpe encoded file:
# * filename: the filename it refers to
# * usedBPEModel: name of the bpe-Model used
# * tokens: tokenized source code, for each line there is an array of tokens
# * bpe: for each line there is an array of integers encoding these tokens


def build_bpe_encoded_corpus_file(filename):
    print(filename)
    pass


def run_me(model):
    hparams = model.load_hparams()
    
    time_at_start = datetime.datetime.now()

    filenames = walkFiles(hparams['path'])
    time_after_walkingfiles = datetime.datetime.now()
    
    for filename in filenames:
        build_bpe_encoded_corpus_file(filename)
     
    
    # print some statistics
    print( "===[ The End ]===")
    print( "time at start: " + str(time_at_start))
    print( "time after walking files: " + str(time_after_walkingfiles))
    
    pass

if __name__ == '__main__':
    # "1K-datapoint", "10K-excerpt", "16K-excerpt", "50K-full", "100K-full"
    # model = BPEModel("1K-datapoint") 
    model = BPEModel("10K-excerpt")
    model.load_hparams()
    
    run_me(model)
