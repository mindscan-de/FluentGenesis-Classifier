EACH input should be hashed, so that all buildsteps can be performed when required or emitted results will be retrieved from cache.

* irgendwo sollte der latest build und seine prüfsummen festgehalten werden, um den ML-Buildprozess zu beschreiben und zu cachen, 
  so dass nur die nötigsten Berechnungen vorgenommen werden.
  Die Prozess schritte sollten so funktional wie möglich beschrieben werden.
* Es braucht ein Buildsystem für Daten, nicht nur für source code
* Auch kann es sein, dass die Daten vom source code abhägen.... (weil die daten ja anders, (bspw mit anderen Algorithmen) verarbeitet werden könnten.)
* Wir wollen beschreiben, wohin das ganze deployt werden sollte / verzeichnisse,
* Wollen wir auch beschreiben, wie das Modell dann gestartet wird
* Sollten für den Buildprozess auch Services referenziert werden können, damit man, weiss, welche Services benötigt werden?
* Wäre es nicht besser dafür eine grafische repräsentation zu haben?
* each component should be individually versionized, so that dependencies to the data can be detetcted and recalculated
* we need ML-Pipeline as code / and we must describe, how the dependencies within the code change/alter/affect the data
* we should be able to describe, which capabilities a buildstep should ask for...
* a data buildsystem should see, what changed and then rebuild the whole data, maybe even from scratch... 
 

Step: "select hparams"
  * value: "16k-full"
  * inputs: "hparams.json"
  * emits:
    * model.*,


TODO:
  * die statistik hängt vom tokenizer und vom set (datapoint, excerpt, full) ab
  * inputs: model_corpus;
  * emits: global-token-count.json for each set
  * das set liegt derzeit an der falschen Position...
  
   

Step: "build_bpe_vocabulary"
input: ""
execute: python build_bpe_encode_vocabulary
arguments:
  * ModelName: {model.name}
  * Description: "This step will do different steps in between. 
    * First: Calculate a dictionary of all java tokens.
      * inputs: model.raw_java_source_code (*.java)
      * emits: global-token-count.json
    * Second: Process these javatokens to emit two files
      * inputs: global-token-count.json
      * emits: tokens.json; vocab.bpe.json
  * Dependencies:
  * rebuild when: source changed(build_bpe_encode_vocabulary, bpe_model, 

      
Step: "encode_model_raw_java_source_code with bpe-statistics"
  * inputs: model.raw_java_source_code; tokens.json; vocab.bpe.json (*.java)
  * emits: model.bpe_encoded_source_code (*.java.json)
  * prozess sollte das ausgabe verzeichnis bestimmen.
  

Step: "calculate_embeddings"
  * inputs: model_bpe_encoded_source_code (*.java.json)
  * parameters: epochs, windowsize, output_dimensions, 
  * emits: embeddings_{model.name}_w{model.windowsize}_{model.embedding_dimensions}d.zip

Step: "build_nextlineofSource_trainngsset"
  * inputs: model.raw_java_source_code (*.java), tokens.json, vocab.bpe.json
  * uses: thetransformer
  * emits: tensorflowmodel(nextlineofsource.chkpt) 
  
Step: "build methodnames_trainingset"
  * inputs: model.raw_java_source_code (*.java); tokens.json; vocab.bpe.json
  * emits: lists of method_names and their contents with masked methodname.json
  
Step: "build bpe_encoded_methodnames_trainingset"
  * inputs: lists of method_names and their contents with masked methodname.json
  * emits: lists bpeencodings of method_names and their contents with masked methodname.json
  
Step: "build_manyother_trainingssets"
  * inputs: tokens.json, vocab.bpe.json
  *emits:
  