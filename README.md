# FluentGenesis-Classifier

## The basic Idea

I want to classify SourceCode (maybe) with a CNN. Later do some work with CNN + RNN. After that I want to work on
Source-Code-Generation. Let's call one of the milestones "SC(L)U" (Source Code (Language) Understanding) in
comparison to NLU (Natural Language Understanding).

* Reading code and writing code can be understood as an NMT task. 
* Maybe GANs can be used to train source code generation. 
* Maybe Use ProGAN methods applied to source code


I recently learned anout "TabNine - Autocompletion with deep learning" through "Two Minute Papers". It seems I'm
not the only one, thinking about the quality of the developer's tools. (see: https://tabnine.com/blog/deep ) And
it seems I'm not the only one, who thinks about code autocompletion using the GPT-2 architecture.

## Technologies

I will definetly make use of
 
* Tensorflow and
* Keras

in this project.

## Datasets to be used

* GLOVE
  * https://nlp.stanford.edu/projects/glove/
    * http://nlp.stanford.edu/data/glove.840B.300d.zip
    * http://nlp.stanford.edu/data/glove.42B.300d.zip
    * http://nlp.stanford.edu/data/glove.6B.zip (Proof of concept)
* GitHub Java Corpus (Problem here is, that the corpus is quite old (2013), syntactically this Java is a bit old, and may be not state of the art) But anyway, it is still good enough for the proof of concept
  * http://groups.inf.ed.ac.uk/cup/javaGithub/
    * Features:
    * Projects: 10.968 (train) 3.817 (test)
    * LOC: 264.255.189 (train) 88.087.507 (test)
    * Tokens: 1.116.195.158 (train) 385.419.678 (test)

## Algorithms to use

* BPE - Will use Byte-Pair-Encoding techniques to calculate "common words" (and also the tokens for the embedding) (unsupervised)
* Word2Vec / Glove or something similar to calculate vector embeddings from co-occurence Matrixes (unsupervised)
* Encoder-Decoder-Model (some Transformer-Model) (maybe GPT, BERT, GPT-2, "Attention is all you need")


## Some Pointers and reminders

* Use natural language embeddings like __glove.6b.300d.txt__ -> better understand variable names / method names
* Some Architecture on classifying source code / text
  * http://blog.aylien.com/source-code-classification-using-deep-learning/
  * https://medium.com/@TalPerry/convolutional-methods-for-text-d5260fd5675f
  * https://medium.com/@TalPerry/announcing-lighttag-the-easy-way-to-annotate-text-afb7493a49b8
  * https://medium.com/@TalPerry
  * https://medium.com/coinmonks/celebrity-face-generation-using-gans-tensorflow-implementation-eaa2001eef86
  * https://towardsdatascience.com/progan-how-nvidia-generated-images-of-unprecedented-quality-51c98ec2cbd2
  * https://research.nvidia.com/sites/default/files/pubs/2017-10_Progressive-Growing-of/karras2018iclr-paper.pdf
  * https://github.com/perplexingpegasus/ProGAN
  * https://www.tngtech.com/fileadmin/Public/Images/BigTechday/BTD11/Folien/MachineLearningonSourceCode.pdf
  * https://arxiv.org/pdf/1809.07945.pdf
  
## This is *not* implementing this paper
But is for whatsoever reason listed as such. Hopefully this github page will be delisted on paperswithcode. 
 
  * arxiv: 1711.00740.pdf
