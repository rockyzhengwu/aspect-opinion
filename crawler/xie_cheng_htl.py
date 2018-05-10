#/usr/bin/env python
#-*-conding:utf-8-*-

"""
携程酒店评论
"""

import requests
import re
import os
import random
import time
import json
import copy
from bs4 import BeautifulSoup

def load_param(path):
    param = {}
    f = open(path)
    for line in f.readlines():
        line = line.strip("\n").strip()
        if not line:
            continue
        line = line.split(":")
        key = line[0]
        v = line[1]
        param[key] = v
    f.close()
    return param

class XieChengHotelCrawler(object):
    def __init__(self, param_path):
        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36 OPR/36.0.2130.65",
                   "Referer":"http://hotels.ctrip.com/hotel/2108742.html?"
                   }
        self.req = requests.Session()

        self.hotel_list_url = "http://hotels.ctrip.com/Domestic/Tool/AjaxHotelList.aspx"
        self.param = load_param(param_path)
        self.req.headers.update(self.headers)
        print(self.param)

    def _parse_hotel_hist(self, html):
        soup = BeautifulSoup(html, "html5lib")
        hotel_new_list = soup.find_all("div", attrs={"class":"hotel_new_list"})
        if not hotel_new_list:
            print("no hotel_new_list")
            return []
        res_htol = []
        for ht in hotel_new_list:
            hotel_id = ht.get("id")
            comment_count = ht.find("span", attrs={"class":"hotel_judgement"})
            if comment_count:
                comment_count = re.search("\d+", comment_count.get_text())
                comment_count =  comment_count.group() if comment_count else 0
            else:
                comment_count = 0

            res_htol.append({"hotel_id":hotel_id, "comment_count":comment_count})
        return res_htol


    def crawl_hotel_list_page(self ):
        try:
            res = self.req.post(self.hotel_list_url, data=self.param )
            res_data = res.json()
        except Exception as e:
            print("request page error")
            print(e)
            return []

        html = res_data.get('hotelList')
        hotel_list = self._parse_hotel_hist(html)
        return hotel_list



    def crawl_hotel_list(self, total_page, outf_path):
        outf = open(outf_path, 'a+')
        for i in range(1, total_page):
            print("page : ", i)
            self.param["page"] = i
            hotel_list = self.crawl_hotel_list_page()
            time.sleep(random.random()*10)
            for ht in hotel_list:
                outf.write(json.dumps(ht, ensure_ascii=False)+"\n")


class HotelCommentCrawler(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36 OPR/36.0.2130.65",
            "Referer": "http://hotels.ctrip.com/hotel/%s.html?isFull=F"
            }
        self.req = requests.Session()

    def crawl_comment(self, hotel_id):
        time.sleep(random.random()*20)
        hotel_url_format = "http://hotels.ctrip.com/hotel/%s.html"
        hotel_url = hotel_url_format%(hotel_id)
        headers = copy.deepcopy(self.headers)
        headers['Referer'] = headers['Referer']%(hotel_id)
        outf = open(os.path.join("comment", hotel_id+".json"), 'w')
        try:
            res = self.req.get(hotel_url, headers=headers)
            html = res.text
            soup = BeautifulSoup(html, 'html5lib')
            comment_div = soup.find("div", attrs={"class":"comment_detail_list"})
            comment_div_list = comment_div.find_all("div", attrs={"class":"comment_block J_syncCmt"})
            for div in comment_div_list:
                text_div =  div.find("div", attrs={"class":"J_commentDetail"})
                comment_text = text_div.get_text()
                comment_title = div.find("span", attrs={"class":"small_c"})
                comment_score_text = comment_title.get("data-value")
                comment_score_dict = comment_score_text.split(",")
                comment_score_dict = [t.split(":") for t in comment_score_dict]
                comment_score_dict = {k:v for (k, v) in comment_score_dict}
                comment_tmp = {"content": comment_text, "score":comment_score_dict}
                outf.write(json.dumps(comment_tmp, ensure_ascii=False)+"\n")
        except Exception as e:
            print(e)
        outf.close()

    def crawl(self, hotel_list_file_path):
        f = open(hotel_list_file_path,'r')
        for i, line in enumerate(f):
            hotel_info = json.loads(line)
            hotel_id = hotel_info.get("hotel_id")
            comment_count = int(hotel_info.get("comment_count"))
            if not comment_count:
                continue
            print("%d  ,  hotel: %s" %(i, hotel_id))
            self.crawl_comment(hotel_id)
        f.close()






if __name__ == '__main__':

    # crawler = XieChengHotelCrawler("./params")
    # crawler.crawl_hotel_list(500, './hotel_list.json')
    comment_crawler = HotelCommentCrawler()
    comment_crawler.crawl("./hotel_list.json")
