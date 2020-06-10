from bs4 import BeautifulSoup as soup
import requests
import time
import json
import selenium
import codecs
import os
import random
from selenium import webdriver
import requestium
from requestium import Keys,Session
import time
from selenium.webdriver.chrome.options import Options
import threading
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from threading import Thread
from requestium import Session, Keys

chrome_options = Options()
chrome_options.add_argument("--headless")
base_url = "SITEURL"
keywords = ["blue","hoodie"]
size = "small"
session = requests.session()
random_size = True
products = json.dumps({'key1': 'a', 'key2': 'a'})
search_delay = 1
p = ""
email = "PAYPAL LOGIN"
password= "PAYPAL PASSWORD"
p_name = ""
signinTime = 0
chromedriver = os.getcwd()+'/chromedriver'
browser = webdriver.Chrome(chromedriver)


def initalLogin():
    global signinTime
    browser.get("https://www.paypal.com/signin?country.x=US&locale.x=en_US")
    email = browser.find_element_by_xpath('//*[@id="email"]')
    email.send_keys(email)
    browser.find_element_by_xpath('//*[@id="btnNext"]').click()
    time.sleep(1)
    password = browser.find_element_by_xpath('//*[@id="password"]')
    password.send_keys(password)
    browser.find_element_by_xpath('//*[@id="btnLogin"]').click()

    while(browser.current_url == "https://www.paypal.com/signin?country.x=US&locale.x=en_US"):
        print("waiting")
        time.sleep(10)
    for cookie in browser.get_cookies():
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)
    print("cookies updated")
    signinTime = time.time()
    r = session.get("https://www.paypal.com/myaccount/home")

def secondLogin():
    browser.get('https://www.paypal.com/signin?returnUri=https%3A%2F%2Fwww.paypal.com%2Fmyaccount&state=%2Fhome')
    email= browser.find_element_by_xpath('//*[@id="email"]')
    password = browser.find_element_by_xpath('//*[@id="password"]')
    email.send_keys(email)
    password.send_keys(password)
    browser.find_element_by_xpath('//*[@id="btnLogin"]').click()
asdftime = time.time()
def get_products():

    link = "{}/products.json".format(base_url)
    r = session.get(link, verify=False)
    print("Get request- required")
    products_json = json.loads(r.text)
    a = products_json["products"]
    global products
    products = a
    return a

def keyword_search(products, keywords):
    global signinTime
    for product in products:
        keys = 0
        for keyword in keywords:
            if(time.time()-signinTime >= 1200):
                secondLogin()
            if(keyword.upper() in product["title"].upper()):
                keys += 1
                global p_name
                p_name = product["title"]
            if(keys == len(keywords)):
                return product



def find_size(session, product, size):
    for variant in product["variants"]:
        if(size in variant["title"]):
            variant = str(variant["id"])
            return variant
    if(random_size):
        variants = []
        for variant in product["variants"]:
            variants.append(variant["id"])
        variant = str(random.choice(variants))
        return variant


def generate_cart_link(session, variant):

    link =  "{}/cart/{}:1".format(base_url,variant)

    return link



def get_shipping(postal_code, country, province, cookie_jar):

    link = base_url + "//cart/shipping_rates.json?shipping_address[zip]={}&shipping_address[country]={}&shipping_address[province]={}".format(postal_code,country,province)
    r = session.get(link, cookies=cookie_jar, verify=False)
    shipping_options = json.loads(r.text)

    ship_opt = shipping_options["shipping_rates"][0]["name"].replace(' ', "%20")
    ship_prc = shipping_options["shipping_rates"][0]["price"]

    shipping_option = "shopify-{}-{}".format(ship_opt,ship_prc)

    return shipping_option


def add_to_cart(variant):

    link = "{}/cart/add.js?id={}".format(base_url,variant)
    response = session.get(link)

    return response



class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return



requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
start_time = time.time()
full = time.time()
initalLogin()

product = None

productThread = ThreadWithReturnValue(target=get_products)
productThread.start()
products = productThread.join()

print("--- found payment and got products in %s seconds ---" % (time.time() - start_time))
start_time = time.time()
while(product == None):
    product = keyword_search(products, keywords)
    if(product == None):
        time.sleep(search_delay)
        print(looking)

print("--- find product" + p_name +  " in %s seconds ---" % (time.time() - start_time))

start_time = time.time()
asdf = ThreadWithReturnValue(target=find_size, args=(session, product, size))
asdf.start()
variant= asdf.join()

atc = ThreadWithReturnValue(target=add_to_cart, args=(variant,))
atc.start()
r = atc.join()
cj = r.cookies

data = {
    'updates[]':'1',
    'goto_pp':'paypal_express'
}

r = session.post("{}/cart".format(base_url),cookies=cj,data=data)
start_time = time.time()
url = ""
while "paypal" not in url:
    response = session.get(r.history[1].url, cookies=r.history[1].cookies)
    url = response.url

print(url)
print(cj)
session.cookies.update(cj)
print(session.cookies)
print("--- payapl stuff for " + p_name +  " done in %s seconds ---" % (time.time() - start_time))
r = session.get(url, cookies=cj)
r = session.get(url, cookies=cj)
#print(r.text)

browser.get(url)
print(time.time() - asdftime)
