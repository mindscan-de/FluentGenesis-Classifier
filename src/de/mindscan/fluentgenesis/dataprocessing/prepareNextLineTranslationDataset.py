'''
MIT License

Copyright (c) 2020 Maxim Gansert

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

@autor: Maxim Gansert
'''

import argparse
import pandas as pd


from de.mindscan.fluentgenesis.bpe.bpe_model import BPEModel
from de.mindscan.fluentgenesis.bpe.bpe_encoder_decoder import SimpleBPEEncoder
from de.mindscan.fluentgenesis.dataprocessing.translation_dataset import TranslationDataset


# the work to do: read each line from the method dataset and output multiple formatted lines, 
# which do have some constraints and formattings.

# max 8 lines of code?
# output format are files which have line by line correspondence
# from 
# array of - [classname] <delim> [methodname] [method_signature] <delim> [code]
# to
# next ..code..
# each line in each "translation" is json array []

COL_ENCODED_METHOD_SIGNATURE = 'encoded_method_sign'
COL_ENCODED_METHOD_NAME = 'encoded_method_name'
COL_ENCODED_METHOD_BODY = 'encoded_method_body'
COL_LENGTH_ENCODED_METHOD_SIGNATRE = 'length_encoded_method_sign'
COL_LENGTH_ENCODED_METHOD_BODY = 'length_encoded_method_body'
COL_LENGTH_ENCODED_METHOD_NAME = 'length_encoded_method_name'
COL_FILENAME = 'file_name'
COL_CLASSNAME = 'class_name'
COL_METHODNAME = 'method_name'


def build_transation_example_for_current_line(row, current_line):
    # encode row[COL_CLASSNAME] = encoded_classname
    # concatenate 
    # row[COL_ENCODED_METHOD_NAME] + row[COL_ENCODED_METHOD_SIGNATURE]
    #
     
    # TODO: array of tokens of the context and the previous lines, before the 'current_line'
    from_line = []
    
    # array of tokens of the "next"(current_line) line 
    to_line = row[COL_ENCODED_METHOD_BODY][current_line]
    
    return from_line, to_line 


def process_chunk(df, bpe_encoder, translation_dataset):
    print (df.columns)
    for _, row in  df.iterrows():
        # TODO: use the bpe encoder to encode the class name and the delimiters / 
        #       because the classname was not encoded in the first place...
        
        num_lines = len(row[COL_ENCODED_METHOD_BODY])
        for current_number in range(1,num_lines):
            translate_from, translate_to = build_transation_example_for_current_line(row, current_number)
            # add the current line as a translation to our dataset
            translation_dataset.addTranslation( translate_from, translate_to )
    pass


def process_all_lines_in_next_line_dataset(input_dataset_path, bpe_encoder, translation_dataset):
    # open jsonl file
    with open(input_dataset_path,'r') as jsonl_file:
        # read chunks with chunksize
        reader = pd.read_json(jsonl_file, lines=True, chunksize=1000)
        for chunk_df in reader:
            # process the dataframe
            process_chunk(chunk_df, bpe_encoder, translation_dataset)


def doWork(bpe_model_name, bpe_directory, input_dataset_path):
    model = BPEModel(bpe_model_name, bpe_directory)
    model.load_hparams()

    model_vocabulary = model.load_tokens()
    model_bpe_data = model.load_bpe_pairs()

    # for encoding the classnames.     
    bpe_encoder = SimpleBPEEncoder(model_vocabulary, model_bpe_data)
    
    # TODO: extract these constants to the args/argparser.
    translation_dataset = TranslationDataset(dataset_name = 'NextLineTranslationDataset.jsonl')
    translation_dataset.prepareNewDataset(dataset_directory = 'D:\\Downloads\\Big-Code-excerpt\\')

    process_all_lines_in_next_line_dataset(input_dataset_path, bpe_encoder, translation_dataset)
    
    translation_dataset.finish()
    
    pass


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Create the translation dataset from "NextLine" dataset.')
    
    parser.add_argument('--input-dataset', dest='input_dataset_path', help='This is the path to the input dataset file containing the next line dataset', default='D:\\Downloads\\Big-Code-excerpt\\methodNextLineDataset.jsonl' )
    parser.add_argument('--bpe-model-dir', dest='bpe_model_directory', help='Path to the BPE directory containing the Model folder', default='../bpe/')
    parser.add_argument('--bpe-model', dest='bpe_model', help='the BPE-Model to use e.g. "16K-full"', default='16K-full')
    # we also need an output filename, where we will write our translations to.

    
    args = parser.parse_args()
    
    print(args)
    
    doWork(bpe_model_name = args.bpe_model, 
           bpe_directory = args.bpe_model_directory, 
           input_dataset_path = args.input_dataset_path )
    
    pass