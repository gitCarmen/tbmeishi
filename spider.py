from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import *
from pyquery import PyQuery as pq
from config import *
import pymongo

client= pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
product_table = db[MONGO_TABLE]

# browser = webdriver.Chrome()
browser = webdriver.PhantomJS(service_args = SERVICE_ARGS)
wait = WebDriverWait(browser,10)

browser.set_window_size(1400,900)
def search():
    print('正在搜索')
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit =  wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
        )
        input.send_keys(KEYWORDS)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total'))
        )
        get_products()
        return total.text
    except TimeoutException:
        return search()

def next_page(page_number):
    print('正在翻页')
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number))
        )#判断高亮页面是否为当前页码
        get_products()
    except TimeoutException:
        next_page(page_number)
def get_products():
    print('商品信息')
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item'))
    ) #判断商品模块是否加载成功
    html = browser.page_source
    doc = pq(html) #使用pyquery解析网页
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image':item.find('.pic .img').attr('src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text()[:-3],
            'title':item.find('.title').text(),
            'shop':item.find('.shopname').text(),
            'location':item.find('.location').text(),
            'link':item.find('.title .J_ClickStat').attr('href'),

        }
        if (item.find('.icon-service-duliang')):
            product['unit_price']= item.find('.icon-service-duliang').text()
        if(item.find('.title .baoyou-intitle')):
            product['delivery']= '包邮'
        print(product)

        save_to_mongo(product) #存储到数据库

def save_to_mongo(result):
    try:
        if product_table.insert(result):
            print('存储到MONGODB成功',result)
    except Exception:
        print('存储到MONGODB失败',result)
def main():
    try:
        total = search()
        print(total)
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2,total+1):
            next_page(i)
    except Exception:
        print('出错啦')
    finally:
        browser.close()

if __name__ == '__main__':
        main()
