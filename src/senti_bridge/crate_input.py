#/usr/bin/env python
#-*-conding:utf-8-*-

source_path = "../../crawler/all_comment.txt"

outf_path = "input.json"

outf = open(outf_path, 'w')

input_f = open(source_path)

import fool
import json

for i, line in enumerate(input_f):
    line = line.strip("\n").strip()
    if not line:
        continue
    tag_words = fool.pos_cut(line)
    tag_list = [item[1] for item in tag_words]
    words_list = [item[0] for item in tag_words]
    outf.write(json.dumps({"words":words_list, "tag":tag_list }, ensure_ascii=False)+"\n")

