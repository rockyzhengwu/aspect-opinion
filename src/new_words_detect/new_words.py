#/usr/bin/env python
#-*-conding:utf-8-*-

"""
新词发现，左右熵+互信息
"""
# 需要发现的词或字的长度

import math
import pickle
import json
import jieba

class Node(object):
    """
    trie node
    """
    def __init__(self, word, count=0, deepth=0):
        self.word = word
        self.count =  count
        self.deepth = deepth
        self.next = {}

class  Trie(object):
    def __init__(self, max_deepth):
        self.root = Node("")
        self.max_deepth = max_deepth

        # 记录每个深度上的词的总数
        self.deep_count = {}

    def add_ngram(self, ngram):
        parent = self.root
        n = len(ngram)
        if not n:
            print("no countent")
            return False
        for i in range(n):
            w = ngram[i]
            if w not in parent.next:
                node = Node(word=w, count=0, deepth=i)
                parent.next[w] = node
            parent = parent.next[w]
        parent.count += 1

        if n not in self.deep_count:
            self.deep_count[n] = 0
        self.deep_count[n] += 1

        return True


    def add_ngram_list(self, ngram_list):
        for ngram in ngram_list:
            self.add_ngram(ngram)


    def get_word_count(self, word):
        """
        整个word出现的次数是word中最后一个词的位置的次数
        :param word:
        :return:
        """
        parent = self.root
        count = 0
        word_len = len(word)
        for i in range(word_len):
            w = word[i]
            if w not in parent.next:
                return count
            parent=parent.next[w]
        count = parent.count
        return count

    def get_entry(self, word):
        """
        查询word 下的子路径
        :param word:
        :return:
        """

        word_len =  len(word)
        parent = self.root
        for i in range(word_len):
            w = word[i]
            if w not in parent.next:
                print("not in trie")
                return 0.0
            parent  = parent.next[w]
        child_count = sum([item.count for item in parent.next.values()])
        child_count = float(child_count)
        entry = 0.0
        for k, node in parent.next.items():
            p = node.count / child_count
            entry -= p*math.log2(p)
        return entry


    def get_word_prob(self, word, min_count=1):
        word_count = self.get_word_count(word)
        # print(word, word_count)
        if not word_count:
            word_count = 1.0
        prob = word_count / self.deep_count.get(len(word))
        return prob

    @staticmethod
    def dump(obj, path):
        f = open(path, 'w')
        pickle.dump(obj, f)

    @staticmethod
    def load(path):
        obj = pickle.load(open(path))
        return obj



class NewWordsCaculator(object):
    """
    构建trie树，并计算pmi 和 entry
    """
    def __init__(self, max_ngram):
        self.preffix_trie = Trie(max_deepth=max_ngram)
        self.reverse_preffix_trie = Trie(max_deepth=max_ngram)
        self.max_ngram = max_ngram


    def _crate_preffix(self, text):
        """
        所有可能前缀
        :param text: str
        :return:
        """
        preffix_list = []
        text_len = len(text)
        for i in range(text_len):
            for j in range(1, self.max_ngram+1):
                if i+j<=text_len:
                    preffix = text[i:i+j]
                    # print(preffix)
                    preffix_list.append(preffix)
        return preffix_list

    def _create_reverse_preffix(self, text):
        return self._crate_preffix(text[::-1])


    def add_words_to_trie(self, text):
        ## 所有的 ngram 存到trie 中
        preffix_list = self._crate_preffix(text)
        self.preffix_trie.add_ngram_list(preffix_list)
        reverse_preffix_list = self._create_reverse_preffix(text)
        self.reverse_preffix_trie.add_ngram_list(reverse_preffix_list)


    def caculate_pmi(self, word_left, word_right):
        prob_left = self.preffix_trie.get_word_prob(word_left)
        prob_right = self.preffix_trie.get_word_prob(word_right)
        prob_join = self.preffix_trie.get_word_prob(word_left + word_right)
        # print(prob_left, prob_right, prob_join)
        pmi = math.log2(prob_join / (prob_left * prob_right))
        return pmi


    def caculate_entry(self, word):
        right_entry = self.preffix_trie.get_entry(word)
        left_entry = self.reverse_preffix_trie.get_entry(word[::-1])
        return left_entry, right_entry

    @staticmethod
    def dump(obj, path):
        f = open(path, 'wb')
        pickle.dump(obj, f)
        f.close()

    @staticmethod
    def load( path):
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        return obj


class WordsDis(object):
    def __init__(self, source_path, caculator_path, out_path, max_ngram=5 , is_cut=False, user_dict=None, stopwords_path=None):
        self.max_ngram = max_ngram
        self.caculator_path = caculator_path
        self.caculator = None
        self.source_path  = source_path
        self.candidate = {}
        self.out_path = out_path
        self.user_dict = user_dict
        self.stopwords_path = stopwords_path
        self.stopwords = []
        self.is_cut = is_cut

        if not os.path.exists(self.caculator_path):
            self.caculator = NewWordsCaculator(max_ngram=self.max_ngram)
            print("start create caculator.....")
            self.crate_caculator(source_path)
            NewWordsCaculator.dump(self.caculator, self.caculator_path)
        else:
            print("load caculator .... ")
            self.caculator = NewWordsCaculator.load(self.caculator_path)


        self._load_stop_words()
        if is_cut and user_dict:
            jieba.load_userdict(user_dict)

    def _load_stop_words(self):
        if not self.stopwords_path:
            return
        with open(self.stopwords_path) as f:
            for i,line in enumerate(f):
                word = line.strip("\n")
                self.stopwords.append(word)

    def cut_words(self, line):
        if self.is_cut:
            words = jieba.cut(line)
        else:
            words = list(line)
        words = [w for w in words if w not in self.stopwords_path]
        return words

    def crate_caculator(self, source_path):
        with open(source_path) as f:
            for i, line in enumerate(f):
                line = line.strip("\n")
                words = self.cut_words(line)
                text = "".join(words)
                self.caculator.add_words_to_trie(text)
                self.add_candidate(words)


    def init_candidate(self):
        with open(self.source_path) as f:
            for i, line in enumerate(f):
                line = line.strip("\n")
                words = self.cut_words(line)
                self.add_candidate(words)

    def add_candidate(self, text):
        text_len = len(text)
        for i in range(text_len-2):
            left  = text[i]
            right = text[i+1]
            bi = left + "_" + right
            if bi not in self.candidate:
                self.candidate[bi] = {}

    def caculate_all(self):
        for k in self.candidate:
            left, right = k.split("_")
            pmi = self.caculator.caculate_pmi(left, right)
            left_entry, right_entry = self.caculator.caculate_entry(left+right)
            self.candidate[k]["pmi"] = pmi
            self.candidate[k]['left_entry'] = left_entry
            self.candidate[k]['right_entry'] = right_entry

    def save_result(self, ):
        f = open(self.out_path, 'w')
        sort_candiate = sorted(self.candidate.items(), key=lambda x:x[1]["pmi"]+x[1]["left_entry"]+x[1]["right_entry"], reverse=True)
        for k, v in sort_candiate:
            out_data = {"words":k, "score":v}
            f.write(json.dumps(out_data, ensure_ascii=False)+"\n")



if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_path", required=True, help="corpus path")
    parser.add_argument("--caculator_path", required=True, help="caculator path, if not exists, will create and save")
    parser.add_argument("--out_path", required=True, help="file to save result")
    parser.add_argument("--user_dict", required=False, help="user dict to load ")
    parser.add_argument("--cut", dest="cut", help="need cut", action="store_true")
    parser.add_argument("--no-cut", dest="cut", help="no cut", action="store_false")
    parser.add_argument("--max_ngram", default=10, type=int, help="the max of ngram save by trie")
    parser.add_argument("--stopwords_path", default=None, help="stopwords file path")
    args = parser.parse_args()

    new_word_distroy = WordsDis(
        source_path = args.source_path,
        caculator_path = args.caculator_path,
        out_path = args.out_path,
        max_ngram = args.max_ngram,
        user_dict = args.user_dict,
        stopwords_path = args.stopwords_path,
        is_cut = args.cut
    )

    new_word_distroy.caculate_all()
    new_word_distroy.save_result()

    # text = "老牌四星，虽然设施稍显成旧，但环境、服务都非常不错，特别值得一提的是早餐，品种丰富，味道也好！另外出行也比较方便，下次来北京还来这！虽然"
    # dwdis = NewWordsCaculator(max_ngram=3)
    # dwdis.add_words_to_trie(text)
    # left_entry, right_entry = dwdis.caculate_entry("虽然")
    # pmi = dwdis.caculate_pmi("虽", "然")
    # print("left_entry: %f, right_entry:%f"%(left_entry, right_entry))
    # print("pmi: ", pmi)
    # ### dump and load ###
    # print("load:  ")
    # NewWordsCaculator.dump(dwdis, "test_nwdis.pkl")
    # new_dwdis = NewWordsCaculator.load("test_nwdis.pkl")
    # pmi = new_dwdis.caculate_pmi("虽", "然")
    # left_entry, right_entry = new_dwdis.caculate_entry("但是")
    # print("left_entry: %f, right_entry:%f"%(left_entry, right_entry))
    # print("pmi", pmi)



