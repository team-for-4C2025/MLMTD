```
Data read over
Dataset size: (2778252, 153)
Label size: (2778252,)
Label distribution:
  brute_force: 1473
  bot: 8686
  ddos: 784068
  dos: 171
  benign: 883629
  infiltration: 2825
  portscan: 166443
  xss: 107
  SSH-Patator: 472519
  FTP-Patator: 458331
Label encoder:
  brute_force: 0
  bot: 1
  ddos: 2
  dos: 3
  benign: 4
  infiltration: 5
  portscan: 6
  xss: 7
  SSH-Patator: 8
  FTP-Patator: 9
[21:21:40] ======== Monitor (0): HostSketchContainer ========
[21:21:40] AllReduce: 0.002756s, 1 calls @ 2756us

[21:21:40] MakeCuts: 0.003011s, 1 calls @ 3011us

[21:21:40] INFO: C:\actions-runner\_work\xgboost\xgboost\src\data\iterative_dmatrix.cc:53: Finished constructing the `IterativeDMatrix`: (2222601, 153, 340057953).
[21:21:40] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
[21:22:37] ======== Monitor (0): GBTree ========
[21:22:37] BoostNewTrees: 53.4944s, 100 calls @ 53494405us

[21:22:37] CommitModel: 0.000295s, 100 calls @ 295us

[21:22:37] ======== Monitor (0): HistUpdater ========
[21:22:37] BuildHistogram: 13.8955s, 4276 calls @ 13895490us

[21:22:37] EvaluateSplits: 0.324534s, 5276 calls @ 324534us

[21:22:37] InitData: 0.33406s, 1000 calls @ 334060us

[21:22:37] InitRoot: 22.8345s, 1000 calls @ 22834489us

[21:22:37] LeafPartition: 0.000224s, 1000 calls @ 224us

[21:22:37] UpdatePosition: 2.77449s, 4847 calls @ 2774486us

[21:22:37] UpdatePredictionCache: 2.6629s, 1000 calls @ 2662902us

[21:22:37] UpdateTree: 40.1841s, 1000 calls @ 40184118us

[21:22:37] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
Round 0 get score 1.0
Predicting label...
Calculating probabilities...
Evaluating model...
Calculating scores...
accuracy: 1.0
recall: 1.0
precision: 1.0
F1 score: 1.0
Drawing confusion matrix...
Drawing ROC curve...
test_label_bin shape: (555651, 10), prediction shape: (555651, 10)
Drawing confusion matrix...
[21:22:43] ======== Monitor (0): HostSketchContainer ========
[21:22:43] AllReduce: 0.0022s, 1 calls @ 2200us

[21:22:43] MakeCuts: 0.002282s, 1 calls @ 2282us

[21:22:44] INFO: C:\actions-runner\_work\xgboost\xgboost\src\data\iterative_dmatrix.cc:53: Finished constructing the `IterativeDMatrix`: (2222601, 153, 340057953).
[21:22:44] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
[21:23:40] ======== Monitor (0): GBTree ========
[21:23:40] BoostNewTrees: 52.688s, 100 calls @ 52688034us

[21:23:40] CommitModel: 0.000263s, 100 calls @ 263us

[21:23:40] ======== Monitor (0): HistUpdater ========
[21:23:40] BuildHistogram: 13.6382s, 4270 calls @ 13638227us

[21:23:40] EvaluateSplits: 0.338263s, 5270 calls @ 338263us

[21:23:40] InitData: 0.338858s, 1000 calls @ 338858us

[21:23:40] InitRoot: 22.0009s, 1000 calls @ 22000870us

[21:23:40] LeafPartition: 0.000242s, 1000 calls @ 242us

[21:23:40] UpdatePosition: 2.87522s, 4843 calls @ 2875217us

[21:23:40] UpdatePredictionCache: 2.74157s, 1000 calls @ 2741567us

[21:23:40] UpdateTree: 39.2143s, 1000 calls @ 39214299us

[21:23:40] ======== Monitor (0): Learner ========
[21:23:40] Configure: 0.002011s, 2 calls @ 2011us

[21:23:40] EvalOneIter: 0.001481s, 100 calls @ 1481us

[21:23:40] GetGradient: 3.17298s, 100 calls @ 3172984us

[21:23:40] PredictRaw: 0.029854s, 100 calls @ 29854us

[21:23:40] UpdateOneIter: 56.6996s, 100 calls @ 56699559us

[21:23:40] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
Round 1 get score 1.0
Predicting label...
Calculating probabilities...
Evaluating model...
Calculating scores...
accuracy: 1.0
recall: 1.0
precision: 1.0
F1 score: 1.0
Drawing confusion matrix...
Drawing ROC curve...
test_label_bin shape: (555650, 10), prediction shape: (555650, 10)
Drawing confusion matrix...
[21:23:45] ======== Monitor (0): HostSketchContainer ========
[21:23:45] AllReduce: 0.002617s, 1 calls @ 2617us

[21:23:45] MakeCuts: 0.002765s, 1 calls @ 2765us

[21:23:45] INFO: C:\actions-runner\_work\xgboost\xgboost\src\data\iterative_dmatrix.cc:53: Finished constructing the `IterativeDMatrix`: (2222602, 153, 340058106).
[21:23:45] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
[21:24:40] ======== Monitor (0): GBTree ========
[21:24:40] BoostNewTrees: 51.7126s, 100 calls @ 51712624us

[21:24:40] CommitModel: 0.000261s, 100 calls @ 261us

[21:24:40] ======== Monitor (0): HistUpdater ========
[21:24:40] BuildHistogram: 13.3114s, 4255 calls @ 13311393us

[21:24:40] EvaluateSplits: 0.321057s, 5255 calls @ 321057us

[21:24:40] InitData: 0.336088s, 1000 calls @ 336088us

[21:24:40] InitRoot: 21.9572s, 1000 calls @ 21957172us

[21:24:40] LeafPartition: 0.000255s, 1000 calls @ 255us

[21:24:40] UpdatePosition: 2.76599s, 4825 calls @ 2765989us

[21:24:40] UpdatePredictionCache: 2.65636s, 1000 calls @ 2656362us

[21:24:40] UpdateTree: 38.7166s, 1000 calls @ 38716610us

[21:24:40] ======== Monitor (0): Learner ========
[21:24:40] Configure: 0.000679s, 2 calls @ 679us

[21:24:40] EvalOneIter: 0.001502s, 100 calls @ 1502us

[21:24:40] GetGradient: 3.02539s, 100 calls @ 3025387us

[21:24:40] PredictRaw: 0.030479s, 100 calls @ 30479us

[21:24:40] UpdateOneIter: 55.7457s, 100 calls @ 55745743us

[21:24:40] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
Round 2 get score 1.0
Predicting label...
Calculating probabilities...
Evaluating model...
Calculating scores...
accuracy: 1.0
recall: 1.0
precision: 1.0
F1 score: 1.0
Drawing confusion matrix...
Drawing ROC curve...
test_label_bin shape: (555650, 10), prediction shape: (555650, 10)
Drawing confusion matrix...
[21:24:45] ======== Monitor (0): HostSketchContainer ========
[21:24:45] AllReduce: 0.003693s, 1 calls @ 3693us

[21:24:45] MakeCuts: 0.003821s, 1 calls @ 3821us

[21:24:46] INFO: C:\actions-runner\_work\xgboost\xgboost\src\data\iterative_dmatrix.cc:53: Finished constructing the `IterativeDMatrix`: (2222602, 153, 340058106).
[21:24:46] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
[21:25:49] ======== Monitor (0): GBTree ========
[21:25:49] BoostNewTrees: 59.3295s, 100 calls @ 59329535us

[21:25:49] CommitModel: 0.000258s, 100 calls @ 258us

[21:25:49] ======== Monitor (0): HistUpdater ========
[21:25:49] BuildHistogram: 15.3613s, 4254 calls @ 15361337us

[21:25:49] EvaluateSplits: 0.355317s, 5254 calls @ 355317us

[21:25:49] InitData: 0.35283s, 1000 calls @ 352830us

[21:25:49] InitRoot: 25.3639s, 1000 calls @ 25363937us

[21:25:49] LeafPartition: 0.000229s, 1000 calls @ 229us

[21:25:49] UpdatePosition: 3.02094s, 4817 calls @ 3020937us

[21:25:49] UpdatePredictionCache: 2.83837s, 1000 calls @ 2838372us

[21:25:49] UpdateTree: 44.4778s, 1000 calls @ 44477848us

[21:25:49] ======== Monitor (0): Learner ========
[21:25:49] Configure: 0.000645s, 2 calls @ 645us

[21:25:49] EvalOneIter: 0.001484s, 100 calls @ 1484us

[21:25:49] GetGradient: 2.98561s, 100 calls @ 2985605us

[21:25:49] PredictRaw: 0.029176s, 100 calls @ 29176us

[21:25:49] UpdateOneIter: 54.7292s, 100 calls @ 54729174us

[21:25:49] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
Round 3 get score 0.999998200305948
Predicting label...
Calculating probabilities...
Evaluating model...
Calculating scores...
accuracy: 1.0
recall: 1.0
precision: 1.0
F1 score: 1.0
Drawing confusion matrix...
Drawing ROC curve...
test_label_bin shape: (555650, 10), prediction shape: (555650, 10)
Drawing confusion matrix...
[21:25:54] ======== Monitor (0): HostSketchContainer ========
[21:25:54] AllReduce: 0.00311s, 1 calls @ 3110us

[21:25:54] MakeCuts: 0.003317s, 1 calls @ 3317us

[21:25:55] INFO: C:\actions-runner\_work\xgboost\xgboost\src\data\iterative_dmatrix.cc:53: Finished constructing the `IterativeDMatrix`: (2222602, 153, 340058106).
[21:25:55] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
[21:26:51] ======== Monitor (0): GBTree ========
[21:26:51] BoostNewTrees: 52.9976s, 100 calls @ 52997570us

[21:26:51] CommitModel: 0.000266s, 100 calls @ 266us

[21:26:51] ======== Monitor (0): HistUpdater ========
[21:26:51] BuildHistogram: 13.5516s, 4271 calls @ 13551597us

[21:26:51] EvaluateSplits: 0.329421s, 5271 calls @ 329421us

[21:26:51] InitData: 0.34996s, 1000 calls @ 349960us

[21:26:51] InitRoot: 22.4923s, 1000 calls @ 22492279us

[21:26:51] LeafPartition: 0.000228s, 1000 calls @ 228us

[21:26:51] UpdatePosition: 2.83955s, 4845 calls @ 2839554us

[21:26:51] UpdatePredictionCache: 2.69566s, 1000 calls @ 2695665us

[21:26:51] UpdateTree: 39.5859s, 1000 calls @ 39585936us

[21:26:51] ======== Monitor (0): Learner ========
[21:26:51] Configure: 0.000631s, 2 calls @ 631us

[21:26:51] EvalOneIter: 0.001484s, 100 calls @ 1484us

[21:26:51] GetGradient: 3.58582s, 100 calls @ 3585821us

[21:26:51] PredictRaw: 0.030835s, 100 calls @ 30835us

[21:26:51] UpdateOneIter: 62.9479s, 100 calls @ 62947949us

[21:26:51] DEBUG: C:\actions-runner\_work\xgboost\xgboost\src\gbm\gbtree.cc:131: Using tree method: 0
Round 4 get score 1.0
Storing XGBoost Classifier model...
XGBoost Classifier model saved to D:\code_repository\mtd\model
Calculating probabilities...
Predicting label...
Evaluating model...
Calculating scores...
accuracy: 1.0
recall: 1.0
precision: 1.0
F1 score: 1.0
Drawing confusion matrix...
Drawing ROC curve...
test_label_bin shape: (694568, 10), prediction shape: (694568, 10)
Drawing confusion matrix...

进程已结束，退出代码为 0

Training CNN Classifier...
Epoch 1, Train Loss: 0.3637
Epoch 2, Train Loss: 0.1189
Epoch 3, Train Loss: 0.0920
Epoch 4, Train Loss: 0.0840
Epoch 5, Train Loss: 0.0783
CNN Classifier trained.
CNN Classifier model saved to D:\code_repository\mtd\model\cnn.pth
Evaluating model...
Calculating scores...
accuracy: 0.9662921348314607
recall: 0.9662921348314607
precision: 0.9664293986231396
F1 score: 0.9659909144683069
Drawing ROC curve...
test_label_bin shape: (25187, 11), prediction shape: (25187, 11)
Drawing confusion matrix...

Data read over
finish reading labelled data
Dataset size: (1600943, 153)
Label size: (1600943,)
Label encoder:
  dos: 0
  brute_force: 1
  infiltration: 2
  injection: 3
  benign: 4
  ddos: 5
  bot: 6
  FTP-Patator: 7
  xss: 8
  portscan: 9
  SSH-Patator: 10
Round 0 get score 0.9843155136497506
Evaluating model...
Calculating scores...
accuracy: 0.9837595919909803
recall: 0.9837595919909803
precision: 0.9842352414122681
F1 score: 0.983554762113047
Drawing ROC curve...
test_label_bin shape: (320189, 11), prediction shape: (320189, 11)
Drawing confusion matrix...
Round 1 get score 0.9836783899509353
Evaluating model...
Calculating scores...
accuracy: 0.9839063802941388
recall: 0.9839063802941388
precision: 0.9842282449903977
F1 score: 0.9837294769977468
Drawing ROC curve...
test_label_bin shape: (320189, 11), prediction shape: (320189, 11)
Drawing confusion matrix...
Round 2 get score 0.9834972469385269
Evaluating model...
Calculating scores...
accuracy: 0.9839750396641973
recall: 0.9839750396641973
precision: 0.9842278774175012
F1 score: 0.9837985283114351
Drawing ROC curve...
test_label_bin shape: (320188, 11), prediction shape: (320188, 11)
Drawing confusion matrix...
Round 3 get score 0.9842092770497333
Evaluating model...
Calculating scores...
accuracy: 0.9845465788849052
recall: 0.9845465788849052
precision: 0.9849699559131534
F1 score: 0.9843686961350825
Drawing ROC curve...
test_label_bin shape: (320188, 11), prediction shape: (320188, 11)
Drawing confusion matrix...
Round 4 get score 0.9845340862243432
Storing XGBoost Classifier model...
XGBoost Classifier model saved to D:\code_repository\mtd\model
Evaluating model...
Calculating scores...
accuracy: 0.9843867508501213
recall: 0.9843867508501213
precision: 0.9847953151703613
F1 score: 0.9842012993209182
Drawing ROC curve...
test_label_bin shape: (400237, 11), prediction shape: (400237, 11)
Drawing confusion matrix...
```

D:\code_repository\data\splited_pcap\brute_force\172.16.0.1-192.168.10.50.pcap