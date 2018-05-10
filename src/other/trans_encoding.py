#/usr/bin/env python
#-*-conding:utf-8-*-

"""
修改文件编码另存

"""

import os
import argparse


def trans_file_encoding(input_dir, output_dir):
    for top, dirs, files in os.walk(input_dir):
        for f_name in files:
            f_path = os.path.join(top, f_name)
            out_top = top.replace(input_dir, output_dir)
            if not os.path.exists(out_top):
                os.makedirs(out_top)

            out_path = os.path.join(out_top, f_name)
            outf = open(out_path, 'w')
            inf = open(f_path, encoding="gbk", errors="ignore")
            outf.write(inf.read())
            inf.close()
            outf.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", requried=True, help="input_dir")
    parser.add_argument("--output_dir", required=True, help="output_dir")
    args = parser.parse_args()
    trans_file_encoding(args.input_dir, args.output_dir)

