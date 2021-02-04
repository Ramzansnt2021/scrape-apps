# libraries and files
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import os
import shutil
from os import path

global basedir
basedir = os.path.abspath(os.path.dirname(__file__))

def products(urls):
#         url= 'https://www.router-switch.com/asa5512-k9-p-4613.html'
    # Set headers
    skus = []
    category = []
    brands = []
    prod_ID = []
    sh_descrip = []
    long_descrip = []
    old_prices = []
    sale_prices = []
    Images = []
    GOOGLE_CHROME_BIN = '/app/.apt/usr/bin/google_chrome'
    CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'
    # CHROMEDRIVER_PATH= os.environ.get('CHROMEDRIVER_PATH',r"/app/.chromedriver/bin/chromedriver") 
    # GOOGLE_CHROME_BIN= os.environ.get('GOOGLE_CHROME_BIN', r"/app/.apt/usr/bin/google-chrome")
    
    option = webdriver.ChromeOptions()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")
    option.add_argument("--headless")
    option.add_argument('--disable-gpu')
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--no-sandbox")
    # option.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    option.binary_location = GOOGLE_CHROME_BIN


    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=option)
    
    fp = open(urls,'r', encoding='utf-8')
    url = fp.readlines()
    for links in url:
        driver.get(links)
        driver.implicitly_wait(60)

        breadcrumb = driver.find_elements_by_class_name('main')
        
        for breadcrumbs in breadcrumb:
            soup = BeautifulSoup(breadcrumbs.get_attribute('innerHTML'), 'html.parser')
            cate_list = soup.select('.breadcrumbs')
            for sub_list in cate_list:
                c_list = sub_list.text
                category.append(c_list.replace('\n', ''))
        

        all_sku = driver.find_elements_by_class_name('product-view')

        for sku in all_sku:
            soup = BeautifulSoup(sku.get_attribute('innerHTML'), 'html.parser')

            detail = soup.select('.product-shop')
            for sku in detail:
                try:
                    h1 = sku.select('.product-name')

                    for h in h1:
                        try:
                            pid = h.find('h1', itemprop="name").text
                            prod_ID.append(pid)

                        except Exception as e:
                            pid = None
                        try:
                            sku = h.find('span', itemprop="sku").text
                            skus.append(sku)

                        except Exception as e:
                            sku = None
                        try:

                            brand = h.find('span', itemprop="brand").text
                            brands.append(brand)
                        except Exception as e:
                            brand = None

                        # print( skus + brands + prod_ID)
                except Exception as e:
                    h1 = None
            for desc in detail:
                try:
                    txt = desc.select("table > .data-table,.product-data-table")
                    for d in txt:
                        descrip = d.find("td", itemprop="description").text
                        #                         print("Short Description: ",descrip)
                        sh_descrip.append(descrip)
                        try:
                            op = d.find('td', {'class': 'listprice'}).find('span').text
#                             print("OLD Prices",op)
                            old_prices.append(op)
                        except Exception as e:
                            op = None
                        try:
                            sp = d.find('td', {'class': 'saleprice'}).find('span', {'class': 'regular-price'}).find(
                                'span').text
#                             print("SALE Prices\n",sp)
#                             print("===============")
                            sale_prices.append(sp)
                        except Exception as e:
                            sp = None
                except Exception as e:
                    desc = None

            #                     LONG DESCRIPTION
            details = soup.select("dd > .tab-container, .dd-specification")
            for long_desc in details:
                try:
                    descp = long_desc.find("div", {'class', 'tab-content'})
                    # print(descp)
                    long_descrip.append(descp)
                except Exception as e:
                    descp = None
        #     print(skus) product-img-box
        for img in all_sku:
            soup = BeautifulSoup(img.get_attribute('innerHTML'), 'html.parser')
            #             print(soup.prettify())
            try:
                i = soup.select('div > .product-image')
                for images in i:
                    link = images.find('a')['href']
                    # print(link)
                    Images.append(link)
            except Exception as e:
                i = None


    
    data = {'SKUs': skus, 'Category': category, 'Product ID': prod_ID, 'Brand': brands, 'Description': sh_descrip, 'OLD Price': old_prices,
            'SALE Price': sale_prices, 'Long descriptions': long_descrip, 'Images': Images, }
    
    return data

def product_files(data):
    source = os.path.join(basedir, "static", "uploads",r"scrape.csv")
    df = pd.DataFrame.from_dict(products(data), orient='index')
    df = df.transpose()
    print(df)
    print("Got these many results:", df.shape)

    # file_name = input("Name of the file using CSV extention e.g; master files.csv: ")
    df.to_csv(source , index=False)
    

    return df

# if __name__ == '__main__':
#     scraper = product_files()
#     scraper.run
# print(get_file_links('https://www.router-switch.com/air-band-inst-tl-p-5685.html'))
# product_files('https://www.router-switch.com/air-band-inst-tl-p-5685.html')
# links = ['https://www.router-switch.com/air-band-inst-tl-p-5685.html','https://www.router-switch.com/asa5512-k9-p-4613.html']
# product_files('D://ormusa//cisco-routers//links.txt')
# product_files(links)
