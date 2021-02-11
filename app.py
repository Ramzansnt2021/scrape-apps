from flask import Flask, redirect, url_for, render_template, request, send_from_directory
# libraries and files
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import os, glob, shutil
import shutil
from os import path
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

posts = [
    {
        'author':'Murtaza Abbas',
        'title': 'Cisco Products',
        'Content':'Cisco Routers Files',
        'Created_on':' Dec 09, 2020',
        },
        {
        'author':'Mehwish',
        'title': 'Dell Products',
        'Content':'Dell server files',
        'Created_on':' Dec 20, 2020',
        }
    ]

ALLOWED_EXTS = {"txt"}
UPLOAD_DIRECTORY = basedir + r'/static/uploads'
DOWN_DIRECTORY = basedir + r'/static/downloads'
ACCESS_LINKS = basedir + r'/static/uploads/*.txt'
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY
app.config['DOWN_DIRECTORY'] = DOWN_DIRECTORY
app.config['ACCESS_LINKS'] = ACCESS_LINKS

DOWN_FILE = basedir + r"/static/uploads/scrape.csv"
app.config['DOWN_FILE'] = DOWN_FILE
# UPLOAD_DIRECTORY = os.path.join(basedir,'static', 'uploads')
# DOWN_DIRECTORY = os.path.join(basedir,'static', 'downloads')
# ACCESS_LINKS = os.path.join(basedir, "static", "uploads" ,r'*.txt')

# if not os.path.exists(DOWN_DIRECTORY):
#     os.makedirs(os.path.join(basedir,'static', DOWN_DIRECTORY))

# if not os.path.exists(UPLOAD_DIRECTORY):
#     os.makedirs(os.path.join(basedir,'static', UPLOAD_DIRECTORY))

def check_file(file):
    return '.' in file and file.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

@app.route('/')
def layout():
    return render_template('select.html' )

@app.route('/home', methods=['post', 'get'])
def home():
    error = None
    filename = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "File is not selected"
            return render_template('home.html', error=error)
        
        file = request.files['file']
        filename = file.filename

        if filename == '':
            error = "File name is empty"
            return render_template('home.html', error=error)
        
        if check_file(filename) == False:
            error = "This file isn't allowed"
        elif path.exists(filename):
            # get the path to the file in the current directory
            src = path.realpath(file);
            # rename the original file
            i=1
            for file in os.listdir(file):
                src=file
                dst="new_link_file"+str(i)+".txt"
                os.rename(src,dst)
                i+=1
            return render_template('home.html', error=error)

        

        file.save(os.path.join(UPLOAD_DIRECTORY, filename))
    
    return render_template('home.html', title='Home', filename=filename)

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
#     CHROMEDRIVER_PATH= os.environ.get('CHROMEDRIVER_PATH',r"/app/.chromedriver/bin/chromedriver") 
    GOOGLE_CHROME_BIN= "https://github.com/heroku/heroku-buildpack-google-chrome"

    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")
    option.add_argument("--headless")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--no-sandbox")
    option.binary_location = os.environ.get("GOOGLE_CHROME_BIN") 


    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })
    option.headless = True
    driver = webdriver.Chrome(chrome_options=option, executable_path=os.environ.get("./chromedriver"))
    
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
    fp.close()
    return data

def product_files(data):
    SOURCE = basedir + r"/static/uploads/scrape.csv"
    app.config['SOURCE'] = SOURCE
    df = pd.DataFrame.from_dict(products(data), orient='index')
    df = df.transpose()
    print(df)
    print("Got these many results:", df.shape)

    # file_name = input("Name of the file using CSV extention e.g; master files.csv: ")
    df.to_csv(SOURCE , index=False)
    

    return df

@app.route('/result')
def about():
    list_of_files = glob.glob(ACCESS_LINKS) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    scraper = product_files(latest_file)
    print(scraper)
    
    source = os.path.join(DOWN_FILE)
    destination = DOWN_DIRECTORY
    filename = os.path.basename(source)
    dest = os.path.join(destination,filename)
    shutil.move(source, dest)
    return render_template('about.html', title='Results', scraper=scraper) 

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def downloads(filename):
    # uploads = os.path.join("D:/formsProject/scrape/project/downloads/bot.csv", app.config['downloads'])
    return send_from_directory(DOWN_DIRECTORY, filename=filename, as_attachment=True)

@app.route('/admin')
def admin():
    return redirect(url_for("home"))





if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=True, )
