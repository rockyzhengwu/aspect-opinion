#/usr/bin/env python
#-*-conding:utf-8-*-

f = open("xiyouji.txt", encoding="gbk", errors="ignore")
outf = open("xiyouji_utf8.txt",'w')
for i, line in enumerate(f):
    outf.write(line)

