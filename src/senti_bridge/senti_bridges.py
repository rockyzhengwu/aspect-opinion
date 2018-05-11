#-*-coding:utf:8-*-


"""
无监督提取 实体情感对

https://github.com/rainarch/SentiBridge
"""

import json
import os
import copy
import argparse


N_SET = ['n', 'ns', 'vn', 'nz', 's', 'nr']
A_SET = ['a']

MAX_SENT = 50
MIN_COUNT = 3
MIN_ERROR = 0.0000001


class PatternPair():
    def __init__(self, input_path="", out_dir = ""):
        self.input_path = input_path
        self.out_dir = out_dir
        self.load_path =  os.path.join(out_dir, "pair_pattern.json")
        print(self.load_path)

        self.n_word_dict = {}
        self.a_word_dict = {}
        self.pattern_dict= {}

        self.pair_to_pattern_count = {}
        self.pattern_to_pair_count = {}

        if  os.path.exists(self.load_path):
            self.load_count_from_file(self.load_path)
        else:
            self.read_pattern_from_input()

        self.init_score()
        self.id_to_nword = {v:k for k, v in self.n_word_dict.items()}
        self.id_to_aword = {v:k for k,v  in self.a_word_dict.items()}
        self.id_to_pattern = {v:k for k,v in self.pattern_dict.items()}


    def init_score(self):
        self.C = {}
        for pair in self.pair_to_pattern_count.keys():
            self.C[pair] = 1.0
        self.A = {}
        for pattern in self.pattern_to_pair_count.keys():
            self.A[pattern] = 1.0


    def mutl_matrix_vec(self, matrix, vec):
        res_vec = {}
        for k, v_dict in matrix.items():
            res_vec[k] = 0.0
            for kk, c in v_dict.items():
                res_vec[k] += c * vec.get(kk, 0.0)
        return res_vec


    def norm_vec(self, vec):
        total = sum(vec.values())
        res = {}
        N = len(vec)
        for k, v in vec.items():
            res[k] = (v/total) * N
        return res


    def check_finish(self,v_last, v_now):
        error = 0.0
        is_finish = True
        for k, s in v_last.items():
            err =  abs(s - v_now.get(k))
            if err > 0.00000001:
                is_finish = False
            error += err
        return is_finish, error


    def save_score(self):
        pair_score_f = open(os.path.join(self.out_dir, "pair_scoure.txt"), 'w')
        sc = sorted(self.C.items(), key=lambda x:x[1], reverse=True)
        for k, s in sc:
            words = k.split("_")
            n_word = self.id_to_nword.get(int(words[0]))
            a_word = self.id_to_aword.get(int(words[1]))
            pair_score_f.write("\t".join([n_word, a_word, str(s)])+"\n")


        sc = sorted(self.A.items(), key=lambda x:x[1] ,reverse=True)
        pattern_score_f = open(os.path.join(self.out_dir, "pattern_score.txt"), 'w')

        for k, s in sc:
            pattern = self.id_to_pattern.get(int(k))
            pattern_score_f.write("\t".join([pattern, str(s)])+"\n")


    def train_ranking(self):
        C_last = copy.deepcopy(self.C)
        iter = 0

        while True:
            iter += 1
            A_new = self.mutl_matrix_vec(self.pattern_to_pair_count, C_last)
            A_norm = self.norm_vec(A_new)
            C = self.mutl_matrix_vec(self.pair_to_pattern_count, A_norm)
            C_norm = self.norm_vec(C)
            is_finish, error = self.check_finish(C_norm, C_last)
            C_last = copy.deepcopy(C_norm)
            print("itertor: ", iter, " error: ", error)
            if is_finish:
                self.C = C_norm
                self.A = A_norm
                self.save_score()
                print("finish")
                return

    def read_pattern_from_input(self):
        f = open(self.input_path)
        for i, line in enumerate(f):
            if i % 10000 ==0:
                print("read from souce: ", i)
            data = json.loads(line)
            tags = data.get("tag")
            words = data.get('words')
            sents = self.doc_to_sents(tags, words)
            for sent in sents:
                self.handle_one_sent(sent)
        self.pair_to_pattern_count = self.reduce_count(self.pair_to_pattern_count)
        self.pattern_to_pair_count = self.reduce_count(self.pattern_to_pair_count)

        self.save_count_to_file(self.load_path)


    def reduce_count(self, old_dict):
        new_dict = {}

        for k , v in old_dict.items():
            new_dict [k] = {}
            for kk , c in v.items():
                if c < MIN_COUNT:
                    continue
                new_dict[k][kk] = c
        return new_dict


    def doc_to_sents(self, tags, words):
        res = []
        sent = []
        for i, (tag, word) in enumerate(zip(tags, words)):
            if tag.startswith("w"):
                if sent:
                    sent_len = MAX_SENT if len(sent) > MAX_SENT else len(sent)
                    res.append(sent[:sent_len])
                    sent = []
            else:
                sent.append([tag, word])
        return res

    def handle_one_sent(self, sent):
        n_info = {}
        a_info = {}
        for i, (tag, word) in enumerate(sent):
            if tag in N_SET:
                n_info[i] = word

            if tag in A_SET:
                a_info[i] = word

        if not all([n_info, a_info]):
            return []

        for n_index, n_word in n_info.items():
            if n_word not in self.n_word_dict:
                self.n_word_dict[n_word] = len(self.n_word_dict)
            for a_index, a_word in a_info.items():
                if a_word not in self.a_word_dict :
                    self.a_word_dict[a_word] = len(self.a_word_dict)
                pair = "_".join((str(self.n_word_dict.get(n_word)), str(self.a_word_dict.get(a_word))))

                if n_index < a_index:
                    pattern = sent[a_index +1 : a_index-1]
                    pattern = "".join([item[1] for item in pattern]) + "+"
                else:
                    pattern = sent[a_index+1: n_index-1]
                    pattern = "".join(item[1] for item in pattern) + "-"
                if pattern not in self.pattern_dict:
                    self.pattern_dict[pattern] = len(self.pattern_dict)

                pat = self.pattern_dict.get(pattern)

                if pair not in self.pair_to_pattern_count:
                    self.pair_to_pattern_count[pair] = {}

                self.pair_to_pattern_count[pair][pat]  = self.pair_to_pattern_count[pair].get(pat, 0.0) + 1

                if pat not in self.pattern_to_pair_count:
                    self.pattern_to_pair_count[pat] =  {}
                self.pattern_to_pair_count[pat][pair] = self.pattern_to_pair_count[pat].get(pair, 0.0) + 1


    def save_count_to_file(self, path):
        outf = open(path, 'w')
        json.dump({
            "n_word_dict":self.n_word_dict,
            'a_word_dict':self.a_word_dict,
            "pattern_dict":self.pattern_dict,
            "pattern_to_pair_count":self.pattern_to_pair_count,
            "pair_to_pattern_count":self.pair_to_pattern_count
        }, outf, ensure_ascii=False)

    def load_count_from_file(self, path):
        data = json.load(open(path))
        self.n_word_dict = data['n_word_dict']
        self.a_word_dict = data['a_word_dict']
        self.pattern_dict = data['pattern_dict']
        self.pattern_to_pair_count = data['pattern_to_pair_count']
        self.pair_to_pattern_count = data['pair_to_pattern_count']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_path", help="source file, every line is json format {'tag':[], 'words':[]}")
    parser.add_argument("--out_dir", help="temp file and result file path")
    args = parser.parse_args()
    source_path = args.source_path
    out_dir = args.out_dir
    obj = PatternPair(input_path=source_path, out_dir=out_dir)
    obj.train_ranking()
