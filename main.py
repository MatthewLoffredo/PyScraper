from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
from time import sleep
import pandas as pd
import requests as rq
import requests.exceptions
import lxml
import re
from product import Product
from models import store as store_to_db
import csv

####################
# for testing
####################
def save_products_to_csv_file(products, file_name):
    with open(file_name, 'w') as csvfile:
        fieldnames = ['name', 'brand', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(len(products)):
            writer.writerow({
                'name': products[i].get("name"),
                'brand': products[i].get("brand"),
                'price': products[i].get("price")
            })

####################
# deletes whitespace in a given string
####################
def get_visible_text(elem):
    result = re.sub('<!--.*-->|\r|\n', '', str(elem), flags=re.DOTALL)
    result = re.sub('\s{2,}|&nbsp;', '', result)
    return result

####################
# joins urls
####################
def join_urls(products):
    base_url = 'https://www.marshalls.com'
    for item in products:
        if item['link'] != '#' and item['link'].strip() != '':
            final_url = base_url + item['link']
            item['link'] = final_url
    return products

####################
# gets info from passed page
####################
def pull_info(driver):
    parse_only = SoupStrainer('div', {'class': "equal-height-row"})
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'product-inner')))
    soup = BeautifulSoup(driver.page_source, "lxml")
    # pattern = "[^-\\s]"
    # soup2 = BeautifulSoup.prettify(soup)
    # print(soup2)
    categories = []
    for el in soup.select_one(".breadcrumbs-container").find_all("li"):
        if el.find("a") is not None:
            if el.find("a").get_text() == "Clearance":
                continue
            categories.append(el.find("a").get_text())
        else:
            categories.append(el.get_text())

    prods = []
    for row in soup.find_all("div", {"class": "product-inner"}):
        try:
            # print(row)
            prods.extend([
                {
                    'link': row.select_one(".product-link").get("href"),
                    'name': row.select_one(".product-title").get_text(),
                    'picture': row.select_one(".product-link").find("img", recursive=False).get("src"),
                    'brand': row.select_one(".product-brand").get_text(),
                    'price': get_visible_text(row.select_one(".price-comparison").previous_element.previous_element.previous_element),
                    'reg_price': row.select_one(".original-price").next_element.next_element.next_element,
                    'provider_id': '',
                    'description': '',
                    'seller_id': 'marshalls.com',
                    'category': str(categories)
                }
                # for row in soup.select(".product-details")
            ])
        except AttributeError:
            print(AttributeError)
    return prods

####################
# goes through all subcategories on sub pages
####################
def sub_tabs(driver):
    preprocess = []
    cat_list = driver.find_element_by_xpath('//ul[@class="category-list"]')
    count = 0
    for link in cat_list.find_elements_by_tag_name('a'):
        ##################
        # saves main window, opens new one from link
        ##################
        new_tab = link.get_attribute('href')
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[2])
        driver.get(new_tab)
        print("Current Page Title is : %s" %driver.title)
        ##################
        # calls function to store info from page
        ##################
        preprocess.extend(pull_info(driver))
        ##################
        # closes window and goes back to source page
        ##################
        driver.close()
        driver.switch_to.window(driver.window_handles[1])
        print("Current Page Title is : %s" %driver.title)
        count += 1
        if count > 0:
            break
    return preprocess

####################
# goes through all category links on main page
####################
def marshalls_parser(driver):
    ####################
    # Close main window overlay
    ####################
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME,"close-modal"))).click()

    ####################
    # Hover over clearance to show hidden view
    ####################
    element_to_hover = driver.find_element_by_id('usmm-tl-cat3620196p')
    hover_action = ActionChains(driver).move_to_element(element_to_hover)
    hover_action.perform()
    time.sleep(2)

    ####################
    # Extract all products in every category
    ####################
    products = []
    count = 0
    for elem in driver.find_elements_by_xpath('//*[@id="usmm-dd-cat3620196p"]/div[1]/div'):
        if count > 0:
            break
        for el in elem.find_elements_by_xpath('.//ul/li'):
            if count > 0:
                break
            for link in el.find_elements_by_tag_name('a'):
                ##################
                # saves main window, opens new one from link
                ##################
                new_tab = link.get_attribute('href')
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(new_tab)
                print("Current Page Title is : %s" %driver.title)
                ##################
                # calls function to store info from page
                ##################
                products.extend(sub_tabs(driver))
                ##################
                # closes window and goes back to source page
                ##################
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("Current Page Title is : %s" %driver.title)
                ##################
                # adds categories to list
                ##################
                count += 1
                if count > 0:
                    break
    driver.close()

    products = join_urls(products)
    store_to_db(products)

    # for i in products:
    #    print(i)

if __name__ == '__main__':
    ##################
    # initilize webdriver and source ur
    ##################
    url = "https://www.marshalls.com/us/store/index.jsp"
    browser = webdriver.Chrome("C:/Users/Matt/chromedriver.exe")
    browser.get(url)

    marshalls_parser(browser)

    #marshalls_parser(browser)
    #data = marshalls_parser(browser)
    #data = pull_info(browser)

    #print(data)
