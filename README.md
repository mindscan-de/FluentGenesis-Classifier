# FluentGenesis-Classifier

## The basic Idea

I want to classify SourceCode with a CNN. Later do some work with CNN + RNN. After that I want to work on
Source-Code-Generation. Let's call one of the milestones "SC(L)U" (Source Code (Language) Understanding) in
comparison to NLU (Natural Language Understanding).

* Reading code and writing code can be understood as an NMT task. 
* Maybe GANs can be used to train source code generation. 
* Maybe Use ProGAN methods applied to source code

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
