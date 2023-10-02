import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import asyncio
import aiohttp
import nest_asyncio
from datetime import datetime,timedelta
from threading import Timer
from urllib.parse import unquote
import mysql.connector
with open('info of database.txt') as p:
    lines=(p.readlines())
    host=lines[0].strip()
    user=lines[1].strip()
    password=lines[2].strip()
    database=lines[3].strip()
    p.close()
try:
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    print("Connected to the database successfully!")
except mysql.connector.Error as err:
    print(f"Error connecting to the database: {err}")

def run_query(query):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(query)
        data = mycursor.fetchall()
        return data
    except mysql.connector.Error as err:
        print(f"Error executing the query: {err}")
        return None
def run_in_query1(query,value):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(query,value)
        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error executing the query: {err}")
        return None

def getlink():
    query='''
        select id
        from book
    '''
    links=[x[0] for x in run_query(query)]
    return links

async def scrapbook(soup,url0):
    books = soup.find_all(class_='product-container well clearfix')[0].find_all(class_='col-md-9 col-sm-9')
    for book in books:
        try:
            product_table = book.find(class_='product-table').find_all('tr')
        except:
            product_table = []
        try:
            for n in range(len(product_table)):
                if 'کد کتاب' in product_table[n].text:
                    book_id = int(product_table[n].text.split(':')[1])
        except:
            book_id=None
        if book_id==url0:
            try:
                price=(int(book.find(class_='price price-broken').text.strip().replace('\n', '').replace(',', '')))
            except:
                try:
                    price=(int(book.find(class_='price').text.strip().replace('\n', '').replace(',', '')))
                except:
                    price=None
            date = datetime.now()
            query="INSERT INTO price_changes (book_id,price,date) VALUES (%s,%s, %s)"
            val = (book_id,price,date)
            run_in_query1(query,val)
            break



semaphore = asyncio.Semaphore(10)
async def fetch(session, url):
    try:
        async with semaphore:
            async with session.get(url) as response:
                response_text = await response.text()
                # print(f"Response from {url}: {len(response_text)} bytes")
                return response_text
    except aiohttp.ClientError as e:
        print(f"Aiohttp ClientError while fetching {url} : {e}")
    except Exception as e:
        print(f"Unexpected error while fetching {url} : {e}")

async def scrape_book(url0):
    url='https://www.iranketab.ir/book/'+str(url0)
    async with aiohttp.ClientSession() as session:
        try:
            html = await fetch(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                await scrapbook(soup,url0)
                return True
            else:
                print(f"Empty response from {url}")
                return 0
        except Exception as e:
            print(f"Error while scraping {url}: {e}")
            return 0

async def run():
    while True:
        if datetime.now().time().hour==15 and datetime.now().time().minute==58 and (20<datetime.now().time().second<30):
            urls = getlink()
            nest_asyncio.apply()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.get_event_loop()
            batch_size = 500
            for j in range(0, len(urls), batch_size):
                batch = urls[j:j + batch_size]
                results = loop.run_until_complete(asyncio.gather(*(scrape_book(url) for url in batch)))
            await asyncio.sleep(15)

loop = asyncio.get_event_loop()
task = loop.create_task(run())
try:
    loop.run_until_complete(task)
except:pass

if mydb.is_connected():
    mydb.close()