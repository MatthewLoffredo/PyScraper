
####################
# reads individual product data
####################
def read_product_data(url):
    #set headers
    headers = rq.utils.default_headers()
    headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

    #get url html
    try:
        url = "https://www.marshalls.com/us/store/shop/clearance/womens-clothing/_/N-3951437597+3255077828?mm=Clearance%3Af%3A+%3A1%3AClothing%3AWomen"
        req = rq.get(url, headers)
        print(req.status_code)
    except HTTPError as http_err:
        print(f'HTTP error occured: {http_err}')
    """
    """
    soup = BeautifulSoup(req.content, 'lxml')
    grid = soup.find_all('a', class_="product-link", limit=1)
    print(grid)
    goods = BeautifulSoup(str(grid), 'lxml')
    tag = goods.select_one(".product-brand")
    #tag = goods.find_all('span', limit=1)
    #grid = soup.find("div", id="product-grid-wrapper")
    #tag = soup.select("product-brand-4000003579")
    print(tag)
