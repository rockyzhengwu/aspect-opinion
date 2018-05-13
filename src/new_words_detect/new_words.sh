#python new_words.py --source_path ../../crawler/all_comment.txt --caculator_path caculator.pkl --out_path words_score.json --stopwords_path stopwords.txt --cut --max_ngram 6
#python new_words.py --source_path xiyouji_utf8.txt --caculator_path xiyouji_caculator.pkl --out_path xiyouji.json --stopwords_path stopwords.txt --no-cut
python new_words.py --source_path /home/rocky/dl/atec-nlp-sim/data/all_sent.txt --caculator_path new_words.pkl --out_path aspt_t.json --stopwords stopwords.txt --max_ngram 10 --cut
