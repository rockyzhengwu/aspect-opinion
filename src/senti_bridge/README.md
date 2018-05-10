## 实体词情感词对提取

### 方法
本文实现的是[rainarch](https://github.com/rainarch/SentiBridge)的方法，
**可能存在理解错误的地方，待验证**

### 使用方法

输入需要分词，每行一个json,每行的格式如下
```
{"tag":[], "words":[]}
```


```
python sent_bridges.py --source_path source_file --out_dir out_dir
```


