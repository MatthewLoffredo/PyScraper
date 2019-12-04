import pymysql


def store(data):
    conn = pymysql.connect(host='APIKEY', user='APIKEY', passwd='APIKEY', db='mysql', charset='utf8')
    try:
        cur = conn.cursor()
        cur.execute("USE ebdb")

        item_bank = []
        for row in data:
            if ' ' in row['price']:
                continue
            item_bank.append((
                row['brand'],
                row['category'],
                row['description'],
                row['link'],
                row['name'],
                row['picture'],
                float(row['price'].replace('$', '').replace(",", '')),
                row['provider_id'],
                float(row['reg_price'].replace('$', '').replace(",", '')),
                row['seller_id']
            )) # append data


        q = """ insert into good (
                brand, category, description, link, name, picture, price, provider_id, reg_price, seller_id)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

        cur.executemany(q, item_bank)
        conn.commit()
        """
        try:
            cur.executemany(q, item_bank)
            conn.commit()
        except:
            print("db insertion unsuccessful")
            conn.rollback()
        """

    finally:
        conn.close()
