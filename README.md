# YoloToolkit
[使用方法](https://qiita.com/kyokio/items/471463bbbb64346adbc3)

## 概要
darknetを使用した物体検出をサポートします。
- VoTTでアノテーションしたxmlファイルをYOLO形式に変更
- `.data`,`.name`ファイルを作成
- train,valid,testにデータを分割

## makedataset.py
`makedataset.py`を実行すると下記がまとめて実行されます。

### ①アノテーションの形式変更(xml->txt)
convert.pyを実行すると以下が実行される
- `xmlファイル`をパースしてYOLOv4形式の`txtファイル`を作成し`YoloDatasetディレクトリ`に保存する  
- `xmlファイル`に対応する`画像ファイル`も`txtファイル`と同時に`YoloDatasetディレクトリ`にコピーする  

### ②データの分割(train,val,test)
アノテーションされたファイルを`train`,`valid`,`test`に分割します。  
デフォルトでは、train=70%,valid=20%,test=10%に分割します。  
※変更したい場合は、`makedataset.py`の`data_split関数`の`train_rate`,`valid_rate`を変更してください。  

各種振り分けられた結果は`cfgディレクトリ`内に`train.txt`,`valid.txt`,`test.txt`が作成され書き込まれます。  

### ③設定ファイルの作成
YOLOv4を実行するのに必要な設定ファイルを作成します。

|ファイル名　|用途　　　　　　　　　　　　　　　|
|:-----------|---------------------------------:|
| .name      |アノテーションされたラベル対応する|
| .data      |class数、各種pathを記入する　　 　|

それぞれ`classes.name`,`test.data`で作成され設定が書き込まれます

## todo
- makedataset.pyの拡張子指定
- makedataset.pyのtest_rate=0のエラー処理
