#　新词发现

## 使用方法

```
python new_words.py --source_path test.txt --caculator_path caculator.pkl --out_path words_score.json --stopwords_path stopwords.txt --no-cu
```

各参数的解释如下:

```
source_path: 源语料文件，格式是一行一个文本
caculator_path: 产生的trie的存储路径
out_path: 最终得分文件的存储路径
user_dict: 用户自定义词典
cut: 需要分词
no-cut: 不要分词
max_ngram: trie存储的ngram的最大长度
stopwords_path: 停用词表的路径
```

## example

运行
```
./new_words.sh
```

然后在当前不目录下产生```words_score.json```


