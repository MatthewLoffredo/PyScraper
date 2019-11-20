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
import csv

def json_format_init():
    return {
        "list": [
            {
            "id": 0,
            "brand": "",
            "category": "",
            "description": "",
            "link": "",
            "name": "",
            "picture": "",
            "price": 0,
            "provider_id": "",
            "reg_price": 0,
            "seller_id": ""
            }
        ]
    }

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
    result = re.sub('\s{2,}|&nbsp;', ' ', result)
    return result

####################
# gets info from passed page
####################
def pull_info(driver):
    parse_only = SoupStrainer(class_='equal-height-row')
    soup = BeautifulSoup(driver.page_source, "lxml", parse_only=parse_only)
    pattern = "[^-\\s]"

    return [
        {
            'name': row.select_one(".product-title").get_text(),
            'brand': row.select_one(".product-brand").get_text(),
            'price': get_visible_text(row.select_one(".price-comparison").previous_element.previous_element.previous_element)
        }
        for row in soup.select(".product-details")
    ]

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
        if count > 1:
            break
        for el in elem.find_elements_by_class_name('sub-menu'):
            if count > 1:
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
                products.extend(pull_info(driver))
                ##################
                # closes window and goes back to source page
                ##################
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                print("Current Page Title is : %s" %driver.title)
                count += 1
                if count > 1:
                    break

    #for item in data['list']:
    #    print(item)
    #save_products_to_csv_file(products, "product_list.csv")
    for i in products:
        print(i)

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

#results = soup.find_all('span', id='product-brand-4000003579')
