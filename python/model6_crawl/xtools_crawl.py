import config

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
from tqdm import tqdm

from sqlalchemy import create_engine
db_connection_str = f"mysql+pymysql://{config.DATABASE_CONFIG['user']}:{config.DATABASE_CONFIG['password']}@{config.DATABASE_CONFIG['host']}/{config.DATABASE_CONFIG['dbname']}"
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()

URL_ADDRESS = "https://xtools.wmflabs.org/articleinfo/en.wikipedia.org/"
LAUNCH_DATE = "/2001-01-01"


def wiki_info_crawl(input_title_list):
    options = Options()
    driver = webdriver.Firefox(options=options,executable_path="python/model6_crawl/geckodriver.exe")

    # 메인화면 >> 로그인화면
    driver.get(URL_ADDRESS)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    login_btn = soup.select_one("a.login-btn")["href"]

    # 로그인
    driver.get(login_btn)

    driver.find_element("id", "wpName1").send_keys(config.xtools_login['id'])
    driver.find_element("id", "wpPassword1").send_keys(config.xtools_login['password'])
    driver.find_element("id", "wpLoginAttempt").click()
    time.sleep(1)

    driver.find_element("name","accept").click()
    time.sleep(1)

    for input_title in tqdm(input_title_list):
        xtools_list = list()
        try:
            time.sleep(1)

            # XTool 검색결과 불러오기
            URL = URL_ADDRESS+input_title+LAUNCH_DATE
            driver.get(URL)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source,"html.parser")

            general_section = soup.select_one("section#general-stats")
            general_tables = general_section.select("table td")
            
            table_list = list()
            table_key_list = list()
            table_value_list = list()

            # 중간 정제 과정
            pretreatment_list = list()
            for index in general_tables:
                if index.has_attr("colspan"):
                    continue
                else:
                    pretreatment_list.append(index)

            # text 가져오기
            for index in pretreatment_list:
                table_list.append(index.get_text().replace("  ","").replace("\n",""))

            # table의 제목과 설명 나누기
            xtools_dict = dict()
            xtools_dict["Title"] = input_title
            for tableData in table_list:
                if table_list.index(tableData) % 2 == 0:
                    table_key_list.append(tableData)
                else:
                    table_value_list.append(tableData)
            
            for i in range(len(table_key_list)):
                xtools_dict[table_key_list[i]] = table_value_list[i]



            year_counts_section = soup.select_one("section#year-counts")
            year_tables = year_counts_section.select("table td.sort-entry--year")
            edits_tables = year_counts_section.select("table td.sort-entry--edits")

            year_list = list()
            edits_list = list()
            for i in year_tables:
                year_list.append(i.get_text())

            for i in edits_tables:
                edits_list.append(i.get_text())
            
            for i in range(len(year_list)):
                xtools_dict[year_list[i]] = edits_list[i]


            xtools_list.append(xtools_dict)
            
            xtools_df = pd.DataFrame(xtools_list)
            xtools_df.to_sql(name='xtools_tb',con=db_connection, if_exists='append', index=False)
        except:
            xtools_dict = dict()
            xtools_dict["name"] = input_title
            xtools_list.append(xtools_dict)
            xtools_df = pd.DataFrame(xtools_list)
            xtools_df.to_sql(name='xtools_tb',con=db_connection, if_exists='append', index=False)
    driver.close()