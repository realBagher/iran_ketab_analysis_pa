import pandas as pd
import mysql.connector
import scipy.stats as stats
from mysql.connector import Error
import streamlit as st
from urllib.parse import quote

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
    st.success("Connected to the database successfully!")
except mysql.connector.Error as err:
    st.error(f"Error connecting to the database: {err}")
    st.stop()

'## Q3 The best publications for printing historical books'

query='''
    select publisher.name as name,count(*) as number_of_books,sum(rate)/count(*) as mean_of_book_rate,sum(price)/count(*) as mean_of_book_price,
       sum(print_series)/count(*) as mean_of_prseries
from book
inner join iranketab.book_tag bt on book.id = bt.book_id
inner join tag on bt.tag_id = tag.tag_id
inner join book_writer on book.id = book_writer.book_id
inner join publisher on book.publisher_id = publisher.id
where tag_title like '%تاریخی%'
group by publisher.id
order by mean_of_prseries DESC ,mean_of_book_price DESC ,mean_of_book_rate DESC ,number_of_books DESC
limit 5
'''
mycursor = mydb.cursor()
mycursor.execute(query)
df0=pd.DataFrame(mycursor.fetchall(),columns=['name','number_of_books','mean_of_book_rate','mean_of_book_price','mean_of_prseries'])
st.dataframe(df0)



'## The second hypothesis test'
try:
    connection = mydb
    query = "SELECT * FROM book"
    data = pd.read_sql_query(query, connection)
    hardcover_data = data[data['cover_type'] == 'جلد سخت']
    softcover_data = data[data['cover_type'] == 'شومیز']

    t_stat, p_value = stats.ttest_ind(hardcover_data['price'], softcover_data['price'])


    if p_value < 0.05:
        text=("There is a significant difference in their prices." )
    else:
        text=("There is no significant difference in their prices.")

except Error as e:
    (f"Database connection error: {e}")

finally:
    if connection.is_connected():
        connection.close()
'### results'
st.code(f't_stat : {t_stat} p_value : {p_value}')
st.subheader('', divider='rainbow')
st.subheader(f'{text}')
with open('Owners_info.txt',encoding='utf8') as p:
    tx=' '.join([n.strip() for n in p])
    p.close()
'### Analysis of the result of the second hypothesis:center'
st.subheader('', divider='red')
st.markdown(f"<p style='text-align: right; color: white;'>{tx}</p>", unsafe_allow_html=True)



