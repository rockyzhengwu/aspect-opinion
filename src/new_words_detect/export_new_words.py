#/usr/bin/env python
#-*-conding:utf-8-*-

words_score_path = "aspt_t.json"
import json

f = open(words_score_path)

for _ , line in enumerate(f):
    data = json.loads(line)
    words = data.get('words')
    word = "".join(words.split("_"))
    print("%s 10000"%(word,))
