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
import json

from com.github.c2nes.javalang import tokenizer

# all the files needs to be recalculated if encoding table is renewed
from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from de.mindscan.fluentgenesis.bpe.bpe_encoder_decoder import SimpleBPEEncoder


# the json file can later be used to calculate the embeddings and also 
# be the source of truth for BERT and other training methods, in the 
# transformer model.

# this should be a producer, which is always retrieves the next file.
def walkFiles(path):
    filenames = []
    for root, _, files in os.walk(path):
        for file_ in files:
            if not file_.endswith(".java"):
                continue
            filenames.append(os.path.realpath(os.path.join(root, file_)))
    return filenames


def runTokenizerForFile(filename):
    with open(filename,"rb") as current_source_file:
        all_lines_as_string = map(lambda line: line.decode('utf-8'), current_source_file.readlines()[0:])
        current_source_code = "".join(all_lines_as_string) 
        return list(tokenizer.tokenize(current_source_code, ignore_errors=False))


# bpe encoded file:
# * bpe: for each line there is an array of integers encoding these tokens


def save_corpus_bpe_content(bpe_content, destination_filename):
    with open(destination_filename, 'w') as bpe_content_file:
        print ("dumping into "+destination_filename)
        json.dump(bpe_content, bpe_content_file, indent=None, sort_keys=True)


def build_bpe_encoded_corpus_file(source_filename, bpe_encoder, model):
    print("encoding: " + source_filename)
    bpe_content = {}
    bpe_content['filename'] = source_filename
    bpe_content['bpeModel'] = model.get_model_name()
    
    #try:

    tokenlist = runTokenizerForFile(source_filename)
    java_tokens = [x.value for x in tokenlist]
    # TODO: later use each line... and encode it for itself
    
    # is this usefull to write the token into the corpus right now? 
    # bpe_content['tokens'] = java_tokens
    
    bpe_data = bpe_encoder.encode( java_tokens )
    bpe_content['bpeTokenData'] = bpe_data
    
    destination_filename = source_filename + ".json";
    save_corpus_bpe_content( bpe_content, destination_filename )
    
    #except:
    #    print("could not encode: "+source_filename) 
    
    pass


def run_me(model):
    hparams = model.load_hparams()
    
    model_vocabulary = model.load_tokens()
    model_bpe_data = model.load_bpe_pairs()
    bpe_encoder = SimpleBPEEncoder(model_vocabulary, model_bpe_data)
    
    time_at_start = datetime.datetime.now()

    filenames = walkFiles(hparams['path'])
    time_after_walkingfiles = datetime.datetime.now()
    
    for filename in filenames:
        build_bpe_encoded_corpus_file(filename, bpe_encoder, model)
     
    
    # print some statistics
    print( "===[ The End ]===")
    print( "time at start: " + str(time_at_start))
    print( "time after walking files: " + str(time_after_walkingfiles))
    
    pass

if __name__ == '__main__':
    # "1K-datapoint", "10K-excerpt", "16K-excerpt", "50K-full", "100K-full"
    # model = BPEModel("1K-datapoint") 
    model = BPEModel("1K-datapoint")
    model.load_hparams()
    
    run_me(model)
