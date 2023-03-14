import model6_crawl.seealso_crawl
import model6_crawl.section_crawl
import model6_crawl.xtools_crawl
import get_db
import config

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

import pymysql
db_connection = pymysql.connect(host=config.DATABASE_CONFIG['host'],
                             user=config.DATABASE_CONFIG['user'],
                             password=config.DATABASE_CONFIG['password'],
                             database=config.DATABASE_CONFIG['dbname'],
                             cursorclass=pymysql.cursors.DictCursor)
cursor = db_connection.cursor()

## fastapi 인스턴스 저장
app = FastAPI()

## static 폴더 mounting작업
app.mount("/static",StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),name="static")

## 템플릿 구성을 위해 Jinja2 활용
templates = Jinja2Templates(directory="templates")

class Item(BaseModel):
    name: str

# 메인페이지
@app.get("/")
def root(request:Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.get("/search")
def root(request:Request):
    seealso_rows = get_db.get_seealso()
    section_rows = get_db.get_section()
    xtools_rows = get_db.get_xtools()
    return templates.TemplateResponse("search.html", {"request":request, "seealso_rows":seealso_rows, "section_rows":section_rows, "xtools_rows":xtools_rows})

@app.post("/crawling_1")
def crawling(request:Request, input_title:Item):
    input_title_list = input_title.name.split(',')
    input_title_list = [v.strip() for v in input_title_list]
    
    cursor.execute('SELECT DISTINCT `from` FROM seealso_tb')
    db_connection.commit()
    data = cursor.fetchall()
    data_list = [v['from'] for v in data]
    print(f'입력 데이터 : {input_title_list}')
    crawl_list = list(set(input_title_list) - set(data_list))
    print(f'중복제거처리 데이터 : {crawl_list}')
    n_step = 2  ##### step차수 = default 3으로 지정
    chain_title_list = list()
    for crawl_title in crawl_list:
        chain_title_list.append(model6_crawl.seealso_crawl.n_char_crawler(crawl_title,n_step))

    chain_title_list = sum(chain_title_list,[])
    return chain_title_list

@app.post("/crawling_2")
def crawling(request:Request, input_title:Item):
    input_title_list = input_title.name.split(',')
    input_title_list = [v.strip() for v in input_title_list]

    cursor.execute('SELECT DISTINCT `title` FROM section_tb')
    db_connection.commit()
    data = cursor.fetchall()
    data_list = [v['title'] for v in data]
    print(f'입력 데이터 : {input_title_list}')
    chain_title_list = list(set(input_title_list) - set(data_list))
    print(f'중복제거처리 데이터 : {chain_title_list}')
    
    for chain_title in chain_title_list:
        model6_crawl.section_crawl.crawl_wiki_by_section(chain_title)

    return input_title_list

@app.post("/crawling_3")
def crawling(request:Request, input_title:Item):
    input_title_list = input_title.name.split(',')
    input_title_list = [v.strip() for v in input_title_list]

    cursor.execute('SELECT DISTINCT `Title` FROM xtools_tb')
    db_connection.commit()
    data = cursor.fetchall()
    data_list = [v['Title'] for v in data]
    print(f'입력 데이터 : {input_title_list}')
    chain_title_list = list(set(input_title_list) - set(data_list))
    print(f'중복제거처리 데이터 : {chain_title_list}')
    
    model6_crawl.xtools_crawl.wiki_info_crawl(chain_title_list)
    
    return None

uvicorn.run(app, host = '0.0.0.0', port = 8000)