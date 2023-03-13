import model6_crawl.seealso_crawl
import model6_crawl.section_crawl
import model6_crawl.xtools_crawl

import time
from tqdm import tqdm

import pymysql
db_connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='vision9551',
                             database='wikipedia_xtools',
                             charset='utf8')
cursor = db_connection.cursor()

def wiki_xtools_crawl(input_title_list):
    start = time.time()
    # input 불러오기 >> input_title_list
    # input_title_list = open("./title_input.txt","r", encoding="utf-8").read().splitlines()
    ##### input_title_list = list(set(input_title_list)) # 중복제거가 필요한 경우가 있으면 주석 풀기
    cursor.execute('SELECT DISTINCT `title` FROM section_tb')
    db_connection.commit()
    data = cursor.fetchall()
    data_list = [v[0] for v in data]
    print(f'입력 데이터 : {input_title_list}')
    print(f'중복제거처리 데이터 : {list(set(input_title_list) - set(data_list))}')
    crawl_list = list(set(input_title_list) - set(data_list))

    n_step = 1  # 반복 회차수 >> n_step

    for crawl_title in crawl_list:
        '''
            모듈화 함수 불러오기 >> model6_crawl.n_char_crawler
        '''
        print(f'\n-----{crawl_title}-----\n')
        wiki_start = time.time()
        chain_title_list = model6_crawl.seealso_crawl.n_char_crawler(crawl_title,n_step)
        # print(chain_title_list)
        wiki_end = time.time()
        print(f'wiki : {wiki_end - wiki_start:.5f} sec')
        
        '''
            모듈화 함수 불러오기 >> section_crawl.crawl_wiki_by_section
        '''
        print('section crawl start')
        section_start = time.time()
        for chain_title in tqdm(chain_title_list):
            model6_crawl.section_crawl.crawl_wiki_by_section(chain_title)
        section_end = time.time()
        print(f'section : {section_end - section_start:.5f} sec')
        '''
            모듈화 함수 불러오기 >> xtools_crawl.wiki_info_crawl
        '''
        print('xtools crawl start')
        xtools_start = time.time()
        model6_crawl.xtools_crawl.wiki_info_crawl(chain_title_list)
        xtools_end = time.time()
        print(f'xtools : {xtools_end - xtools_start:.5f} sec')

    end = time.time()
    print(f'total time : {end - start:.5f} sec')