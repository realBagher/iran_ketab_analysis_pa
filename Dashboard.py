import hazm
import streamlit as st
import pandas as pd
import random
import matplotlib.pyplot as plt
import mysql.connector
import altair as alt
import scipy.stats as stats
import networkx as nx
from pyvis.network import Network
import numpy as np
from PIL import Image
import streamlit.components.v1 as components
from wordcloud import WordCloud
from wordcloud_fa import WordCloudFa
import re
import string
from bertmodel import gettr, recom

with open('info_of_database.txt') as p:
    lines = (p.readlines())
    host = lines[0].strip()
    user = lines[1].strip()
    password = lines[2].strip()
    database = lines[3].strip()
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


def run_query(query):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(query)
        data = mycursor.fetchall()
        return data
    except mysql.connector.Error as err:
        st.error(f"Error executing the query: {err}")
        return None


def q1():
    # 1_Query to get the number of books per tag
    tag_query = """
    SELECT tag.tag_title, COUNT(book_tag.book_id) AS book_count
    FROM tag
    JOIN book_tag ON tag.tag_id = book_tag.tag_id
    GROUP BY tag.tag_title
    HAVING book_count > 2000
    """
    tag_data = run_query(tag_query)
    # Display the number of books per tag as a bar chart
    st.subheader("1. Number of Books per Tag > 2000")
    tag_df = pd.DataFrame(tag_data, columns=["Tag", "Book Count"])
    chart = alt.Chart(tag_df).mark_bar().encode(
        x=alt.X('Tag', sort='-y'),
        y='Book Count'
    )
    st.altair_chart(chart, use_container_width=True)


def q2():
    # 2_query to get the top 10 publishers by book count
    publisher_query = """
    SELECT publisher.name, COUNT(book.id) AS book_count
    FROM publisher
    JOIN book ON publisher.pub_id = book.publisher_id
    GROUP BY publisher.name
    ORDER BY book_count DESC
    LIMIT 10
    """
    publisher_data = run_query(publisher_query)

    # Display the top 10 publishers by book count as a bar chart
    st.subheader("2. Top 10 Publishers by Book Count")
    publisher_df = pd.DataFrame(publisher_data, columns=["Publisher", "Book Count"])
    chart = alt.Chart(publisher_df).mark_bar().encode(
        x=alt.X('Publisher', sort='-y'),
        y='Book Count'
    )
    st.altair_chart(chart, use_container_width=True)


def q3():
    # 3_Query to get the number of books per publication year
    year_query = """
    SELECT solarh_py AS publication_year, COUNT(id) AS book_count
    FROM book
    WHERE solarh_py BETWEEN 1370 AND 1402
    GROUP BY publication_year
    """
    year_data = run_query(year_query)

    # Display the number of books per publication year as a line chart
    st.subheader("3. Number of Books per Publication Year")
    year_df = pd.DataFrame(year_data, columns=["Publication Year", "Book Count"])
    chart = alt.Chart(year_df).mark_line(point=True).encode(
        x='Publication Year',
        y='Book Count'
    )
    st.altair_chart(chart, use_container_width=True)
    year_df["Publication Year"] = year_df["Publication Year"].astype(int)
    year_range = st.slider("Select Year Range", min_value=1370, max_value=1402, value=(1370, 1402))
    filtered_df = year_df[
        (year_df["Publication Year"] >= year_range[0]) & (year_df["Publication Year"] <= year_range[1])]
    chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x='Publication Year',
        y='Book Count'
    )
    st.altair_chart(chart, use_container_width=True)


def q4():
    # 4_Query to get the top 10 writers by book count
    writer_query = """
    SELECT person.name, COUNT(book.id) AS book_count
    FROM person
    JOIN book_writer ON person.person_id = book_writer.writer_id
    JOIN book ON book_writer.book_id = book.id
    WHERE person.name !='مجموعه‌ ی نویسندگان'
    GROUP BY person.name
    ORDER BY book_count DESC
    LIMIT 10
    """
    writer_data = run_query(writer_query)

    # Display the top 10 writers by book count as a bar chart
    st.subheader("4. Top 10 Writers by Book Count")
    writer_df = pd.DataFrame(writer_data, columns=["Writer", "Book Count"])
    chart = alt.Chart(writer_df).mark_bar().encode(
        x=alt.X('Writer', sort='-y'),
        y='Book Count'
    )
    st.altair_chart(chart, use_container_width=True)


def q5():
    # 5_Query to get the top 10 translators by book count
    translator_query = """
    SELECT person.name, COUNT(book.id) AS book_count
    FROM person
    JOIN book_translator ON person.person_id = book_translator.translator_id
    JOIN book ON book_translator.book_id = book.id
    WHERE person.name !='مجموعه ی نویسندگان'
    and person.name !='مجموعه ‌ی مترجمان'
    GROUP BY person.name
    ORDER BY book_count DESC
    LIMIT 10
    """
    translator_data = run_query(translator_query)

    # Display the top 10 translators by book count as a bar chart
    st.subheader("5. Top 10 Translators by Book Count")
    translator_df = pd.DataFrame(translator_data, columns=["Translator", "Book Count"])
    chart = alt.Chart(translator_df).mark_bar().encode(
        x=alt.X('Translator', sort='-y'),
        y='Book Count'
    )
    st.altair_chart(chart, use_container_width=True)


def q6():
    # 6_Query to get a scatter plot of pages vs. publication year
    scatter_query = """
    SELECT num_page, solarh_py AS publication_year
    FROM book
    WHERE num_page IS NOT NULL
    and num_page between 0 and 10000
    AND solarh_py IS NOT NULL
    and solarh_py between 1370 and 1402
    """
    scatter_data = run_query(scatter_query)
    st.subheader("6. Scatter Plot: Pages vs. Publication Year")
    scatter_df = pd.DataFrame(scatter_data, columns=["Pages", "Publication Year"])
    scatter_chart = alt.Chart(scatter_df).mark_circle(size=20).encode(
        x=alt.X("Publication Year", title="Publication Year"),
        y=alt.Y("Pages", title="Number of Pages"),
        tooltip=["Publication Year", "Pages"]
    )
    st.altair_chart(scatter_chart, use_container_width=True)
    scatter_df["Publication Year"] = scatter_df["Publication Year"].astype(int)
    page_range = st.slider("Select Page Range", min_value=0, max_value=10000, value=(0, 10000))
    year_range = st.slider("Select Year Range", min_value=1370, max_value=1402, value=(1370, 1402))
    filtered_df = scatter_df[
        (scatter_df["Pages"] >= page_range[0]) & (scatter_df["Pages"] <= page_range[1]) &
        (scatter_df["Publication Year"] >= year_range[0]) & (scatter_df["Publication Year"] <= year_range[1])
        ]
    scatter_chart = alt.Chart(filtered_df).mark_circle(size=20).encode(
        x=alt.X("Publication Year", title="Publication Year", scale=alt.Scale(domain=[year_range[0], year_range[1]])),
        y=alt.Y("Pages", title="Number of Pages"),
        tooltip=["Publication Year", "Pages"]
    )
    st.altair_chart(scatter_chart, use_container_width=True)


def q7():
    # 7_Query to get a scatter plot of price vs. publication year
    price_query = """
    SELECT price, solarh_py AS publication_year
    FROM book
    WHERE price IS NOT NULL
    and price between 0 and 2000000
    AND solarh_py IS NOT NULL
    and solarh_py between 1370 and 1402
    """
    price_data = run_query(price_query)

    # Display the scatter plot of price vs. publication year
    st.subheader("7. Scatter Plot: Price vs. Publication Year")
    price_df = pd.DataFrame(price_data, columns=["Price", "Publication Year"])
    scatter_chart = alt.Chart(price_df).mark_circle(size=20).encode(
        x=alt.X("Publication Year", title="Publication Year"),
        y=alt.Y("Price", title="Price"),
        tooltip=["Publication Year", "Price"]
    )
    st.altair_chart(scatter_chart, use_container_width=True)
    max_price = price_df["Price"].max()
    min_price = price_df["Price"].min()
    price_range = st.slider("Select Price Range", min_value=min_price, max_value=max_price,
                            value=(min_price, max_price))
    filtered_df = price_df[
        (price_df["Price"] >= price_range[0]) & (price_df["Price"] <= price_range[1])]
    scatter_chart = alt.Chart(filtered_df).mark_circle(size=20).encode(
        x=alt.X("Publication Year", title="Publication Year"),
        y=alt.Y("Price", title="Price"),
        tooltip=["Publication Year", "Price"]
    )
    st.altair_chart(scatter_chart, use_container_width=True)


def q8():
    # 8_Query to get a Price scatter chart based on book rate
    price_query = """
                SELECT rate, price
                FROM book
                where rate between 2.5 and 4.5
                  and price between 0 and 4000000
"""
    price_data = run_query(price_query)

    # Display the Price scatter chart based on book rate
    st.subheader("8. Scatter Plot: Price scatter chart based on book rate")
    df = pd.DataFrame(price_data, columns=['rate', 'price'])
    # chart = alt.Chart(df).mark_circle(size=15).encode(
    #     x=alt.X("rate:Q", title="Rating", scale=alt.Scale(domain=(2.5, 4.5), nice=False)),
    #     y=alt.Y("price:Q", title="Price Of Book"),
    #     tooltip=['rate', 'price']
    # )
    # st.altair_chart(chart, use_container_width=True)

    rate_range = st.slider("Rate Range", min_value=2.5, max_value=4.5, value=(2.5, 4.5), step=0.1)
    price_range = st.slider("Price Range", min_value=0, max_value=4000000, value=(0, 4000000), step=1000)
    filtered_df = df[(df['rate'] >= rate_range[0]) & (df['rate'] <= rate_range[1]) & (df['price'] >= price_range[0]) & (
            df['price'] <= price_range[1])]
    chart = alt.Chart(filtered_df).mark_circle(size=15).encode(
        x=alt.X("rate:Q", title="Rating", scale=alt.Scale(domain=(2.5, 4.5), nice=False)),
        y=alt.Y("price:Q", title="Price Of Book"),
        tooltip=['rate', 'price']
    )
    st.altair_chart(chart, use_container_width=True)


def q9():
    # 9_Query to Chart of the number of books according to the type of cut
    price_query = query = "SELECT size, COUNT(*) as book_count FROM book GROUP BY size"
    price_data = run_query(price_query)

    # Display Chart of the number of books according to the type of cut
    st.subheader("9. Chart: number of books according to the type of cut")
    df = pd.DataFrame(price_data, columns=["Size", "Book Count"])
    chart = alt.Chart(df).mark_bar().encode(
        x="Size:O",
        y="Book Count:Q"
    )
    st.altair_chart(chart, use_container_width=True)


def q10():
    # 10_Query Interactive chart
    st.sidebar.subheader("Advanced Book Search")
    rate_range = st.sidebar.slider("Rate Range", min_value=0.0, max_value=5.0, step=0.1, value=(0.0, 5.0))
    english_title = st.sidebar.text_input("English Title").replace(' ', '%')
    persian_title = st.sidebar.text_input("Persian Title").replace(' ', '%')
    publisher_name = st.sidebar.text_input("Publisher Name").replace(' ', '%')
    min_solarh_py = st.sidebar.number_input("Minimum Solarh Py", min_value=0, step=100, value=0)
    max_solarh_py = st.sidebar.number_input("Maximum Solarh Py", min_value=0, step=100, value=8500)
    tag_titles_list = st.sidebar.text_input("Tag").replace(' ', '%')
    publisher = st.sidebar.text_input("Publisher").replace(' ', '%')
    writer = st.sidebar.text_input("Writer").replace(' ', '%')
    cover = st.sidebar.text_input("Cover Type").replace(' ', '%')
    min_rate, max_rate = rate_range
    # Display Interactive chart
    st.subheader("10. Chart: Interactive chart")
    query = f"""
    SELECT b.rate, b.english_title, b.persian_title, b.publisher_name, b.solarh_py, t.tag_title, p.name, p2.name, b.cover_type
    FROM book AS b
             JOIN publisher AS p ON b.publisher_id = p.pub_id
             JOIN book_tag AS bt ON b.id = bt.book_id
             JOIN tag AS t ON bt.tag_id = t.tag_id
             JOIN book_writer bw on b.id = bw.book_id
             JOIN person p2 on bw.writer_id = p2.person_id AND p2.is_translator = 1
    WHERE 
            b.rate BETWEEN {min_rate} AND {max_rate}
              AND b.english_title LIKE '%{english_title}%'
              AND b.persian_title LIKE '%{persian_title}%'
              AND b.publisher_name LIKE '%{publisher_name}%'
              AND b.solarh_py BETWEEN {min_solarh_py} AND {max_solarh_py}
              AND t.tag_title LIKE '%{tag_titles_list}%'
              AND p.name LIKE '%{publisher}%'
              AND p2.name LIKE '%{writer}%'
              AND b.cover_type LIKE '%{cover}%'
    """
    values = (
    min_rate, max_rate, f"%{english_title}%", f"%{persian_title}%", f"%{publisher_name}%", min_solarh_py, max_solarh_py,
    f"%{tag_titles_list}%", f"%{publisher}%", f"%{writer}%", f"%{cover}%")
    mycursor = mydb.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()

    df = pd.DataFrame(data, columns=['Rate', 'English Title', 'Persian Title', 'Publisher Name', 'Solarh Py', 'Tag',
                                     'Publisher', 'Writer', 'Cover']).drop_duplicates()
    if df.empty:
        st.image('error.png', caption='???????')
    else:
        st.title("Interactive chart (advanced search)")
        st.subheader("Search Results")
        st.dataframe(df)
    mycursor.close()


def q11():
    # Buyer request 1
    price_query = """SELECT b.persian_title,
       p.is_writer          as is_writerr,
       p.name               AS writer_name,
       COUNT(DISTINCT b.id) AS num_books,
       SUM(pd.`like`)       AS total_likes,
       t2.tag_title         as tag,
       b.price              as book_price,
       b.print_series       as print
FROM book b
         JOIN book_tag bt ON bt.book_id = b.id
         JOIN tag t2 ON t2.tag_id = bt.tag_id
         JOIN book_writer bw ON b.id = bw.book_id
         JOIN person p ON bw.writer_id = p.person_id
         JOIN person_description pd ON p.person_id = pd.person_id
WHERE t2.tag_title like '%ع%ش%ق%'
GROUP BY p.is_writer, p.name, t2.tag_title, b.persian_title, b.price, b.print_series
ORDER BY total_likes DESC, num_books DESC
"""
    data = run_query(price_query)

    # Buyer request 1
    st.subheader("Buyer request 1: The best authors of the romance genre")
    df = pd.DataFrame(data,
                      columns=['book name', 'is writer', 'writer name', 'num of books', 'total likes', 'tag name',
                               'price',
                               'print'])
    df0 = df[['writer name']].drop_duplicates().head(5)
    st.dataframe(df0.reset_index()[['writer name']])
    options = st.multiselect("Select View Option", ["Top High Print Series", "Top High Price"])
    if "Top High Print Series" in options:
        sorted_df = df.sort_values(by='print', ascending=False)
        st.dataframe(sorted_df[['writer name']].drop_duplicates().head(5).reset_index()[['writer name']])
    elif "Top High Price" in options:
        sorted_df = df.sort_values(by='price', ascending=False)
        st.dataframe(sorted_df[['writer name']].drop_duplicates().head(5).reset_index()[['writer name']])


def q12():
    # Buyer request 2
    rate_percentile_query = "SELECT rate FROM book ORDER BY rate DESC"
    price_percentile_query = "SELECT price FROM book ORDER BY price ASC"
    rate_results = run_query(rate_percentile_query)
    price_results = run_query(price_percentile_query)
    rate_index = int(len(rate_results) * 0.25)
    price_index = int(len(price_results) * 0.2)
    rate_threshold = rate_results[rate_index][0]
    price_threshold = price_results[price_index][0]
    query = f"""
    SELECT b.id,
           b.ISBN,
           b.persian_title,
           b.english_title,
           b.rate,
           b.price,
           b.print_series,
           pd.`like`
    FROM book b
             JOIN book_writer bw ON b.id = bw.book_id
             JOIN person p on bw.writer_id = p.person_id
             JOIN person_description pd on p.person_id = pd.person_id
    WHERE b.rate >= {rate_threshold}
      AND b.price <= {price_threshold}
    order by rate desc, price asc
    """
    results = run_query(query)
    df = pd.DataFrame(results, columns=['id', 'isbn', 'p_title', 'e_title', 'rate', 'price', 'series', 'like'])
    # Buyer request 2
    st.subheader("Buyer request 2: The best books in the first quarter of quality")
    st.dataframe(df)

    options = st.multiselect("Select View Option", ["Top High Print Series", "Top High Likes"])
    if "Top High Print Series" in options and "Top High Likes" in options:
        like_min = df['series'].min()
        like_max = df['series'].max()
        avg = (like_max - like_min) / 5
        sorted_df = df[(df['series'] >= avg) & (df['series'] <= like_max)].sort_values(by=['series'],
                                                                                       ascending=False)
        st.dataframe(sorted_df)
    elif "Top High Print Series" in options:
        sorted_df = df.sort_values(by='series', ascending=False)
        st.dataframe(sorted_df)
    elif "Top High Likes" in options:
        like_min = df['like'].min()
        like_max = df['like'].max()
        avg = (like_max - like_min) / 5
        sorted_df = df[(df['like'] >= avg) & (df['like'] <= like_max)].sort_values(by='like', ascending=False)
        st.dataframe(sorted_df)


def q13():
    # Author request
    rate_percentile_query = "SELECT rate FROM book ORDER BY rate DESC"
    price_percentile_query = "SELECT price FROM book ORDER BY price ASC"
    rate_results = run_query(rate_percentile_query)
    price_results = run_query(price_percentile_query)
    rate_index = int(len(rate_results) * 0.25)
    price_index = int(len(price_results) * 0.2)
    rate_threshold = rate_results[rate_index][0]
    price_threshold = price_results[price_index][0]
    query = query = '''
    select publisher.name as name,count(*) as number_of_books,sum(rate)/count(*) as mean_of_book_rate,sum(price)/count(*) as mean_of_book_price,
       sum(print_series)/count(*) as mean_of_prseries
from book
inner join book_tag bt on book.id = bt.book_id
inner join tag on bt.tag_id = tag.tag_id
inner join book_writer on book.id = book_writer.book_id
inner join publisher on book.publisher_id = publisher.id
where tag_title like '%تاریخی%'
group by publisher.id
'''
    results = run_query(query)
    df = pd.DataFrame(results,
                      columns=['name', 'number_of_books', 'mean_of_book_rate', 'mean_of_book_price',
                               'mean_of_prseries'])

    # Author request

    st.subheader("Author request: The best publications for printing historical books")

    options = st.multiselect("Select View Option",
                             ["Top High number of books", "Top High mean of book rate",
                              "Top High mean of book price", "Top High mean of book print series"], max_selections=2)
    sorted_df = df
    if options:
        for i in options:
            if "Top High number of books" == i:
                sorted_df = sorted_df.sort_values(by='number_of_books', ascending=False).head(5)
            if "Top High mean of book rate" == i:
                sorted_df = sorted_df.sort_values(by='mean_of_book_rate', ascending=False).head(5)
            if "Top High mean of book price" == i:
                sorted_df = sorted_df.sort_values(by='mean_of_book_price', ascending=False).head(5)
            if "Top High mean of book print series" == i:
                sorted_df = sorted_df.sort_values(by='mean_of_prseries', ascending=False).head(5)
    st.dataframe(sorted_df.reset_index(drop=True).head(5))


def q14():
    # The first hypothesis test
    st.subheader("The first hypothesis test: Untranslated is expensive or translated")
    query_no_translator = """
    SELECT id, persian_title, price
    FROM book
    WHERE id NOT IN (SELECT book_id FROM book_translator)
    """
    query_with_translator = """
    SELECT book.id, book.persian_title, book.price
    FROM book
    JOIN book_translator ON book.id = book_translator.book_id
    """
    alpha = 0.05
    try:
        books_no_translator = run_query(query_no_translator)
        books_with_translator = run_query(query_with_translator)
        prices_no_translator = [book[2] for book in books_no_translator]
        prices_with_translator = [book[2] for book in books_with_translator]
        t_stat, p_value = stats.ttest_ind(prices_no_translator, prices_with_translator)
        st.code(f't_stat : {t_stat} p_value : {p_value} alpha : {alpha}')
        result = ''
        if p_value < alpha:
            result = "There is a significant difference in their prices."
        else:
            result = "There is no significant difference in their prices."
        st.subheader('', divider='rainbow')
        st.subheader(f'{result}')
        st.subheader('', divider='red')
    except mysql.connector.Error as err:
        print("Error executing SQL query:", err)

    st.subheader("The second hypothesis test: Which cover is more expensive?")
    try:
        connection = mydb
        query = "SELECT * FROM book"
        data = pd.read_sql_query(query, connection)
        hardcover_data = data[data['cover_type'] == 'جلد سخت']
        softcover_data = data[data['cover_type'] == 'شومیز']

        t_stat, p_value = stats.ttest_ind(hardcover_data['price'], softcover_data['price'])
        st.code(f't_stat : {t_stat} p_value : {p_value} alpha : {alpha}')
        if p_value < alpha:
            result = ("There is a significant difference in their prices.")
        else:
            result = ("There is no significant difference in their prices.")

        st.subheader('', divider='rainbow')
        st.subheader(f'{result}')
        st.subheader('', divider='green')
        with open('Owners_info.txt', encoding='utf8') as p:
            tx = ' '.join([n.strip() for n in p])
            p.close()
        st.markdown(f"<p style='text-align: right; color: white;'>{tx}</p>", unsafe_allow_html=True)
        st.subheader('', divider='red')
    except mysql.connector.Error as e:
        (f"Database connection error: {e}")


def q15():
    # Graph of tags
    st.subheader("Graph of tags")
    G = nx.Graph()
    query = '''
                select tag_title
                from tag
    '''
    data = run_query(query)
    nod_list = [x[0] for x in data]
    eq = '''
        with a as (
            SELECT
                    bt.tag_id as tid,
                    t.tag_title as tname,
                    bt.book_id as bid
            FROM book_tag as bt
            join tag as t on bt.tag_id = t.tag_id
)
SELECT
a.tname as tname1,
a2.tname as tname2,
COUNT(*) as cral
FROM a
JOIN a as a2 on a.tid
WHERE a.bid=a2.bid and a.tid>a2.tid
GROUP BY tname1,tname2
ORDER BY cral DESC,tname1 ASC
limit 233
    '''
    edata = run_query(eq)
    G.add_nodes_from(nod_list)
    # pos = nx.circular_layout(G, scale=1000)
    # for n in nod_list:
    #     G.add_node(n,
    #                size=5,
    #                x=pos[n][0],
    #                y=pos[n][1],
    #                physics=False)
    for i in edata:
        G.add_edge(i[0], i[1], title=i[2])
    net = Network(height="1000px", width="100%", bgcolor="#222222", font_color="white", notebook=True)
    net.from_nx(G)
    net.show_buttons()
    a = net.generate_html('h.html', local=False)
    components.html(a, width=800, height=600)


def q16():
    # Correlation between book tags
    st.subheader("Correlation between book tags")
    rules_df = pd.read_csv('Confidence.csv')
    t = rules_df.loc[(rules_df.len_act >= 1) & (rules_df.len_cqt == 1)][['cqt']].drop_duplicates().values
    tag_l = [x[0] for x in t]
    li1 = st.multiselect(
        "Select your tag:",
        tag_l, max_selections=3)
    txt = ' '.join([x for x in li1])
    if len(li1) > 0:
        df = rules_df.loc[(rules_df.len_act == len(li1)) & (rules_df.act.str.contains(txt))].sort_values(
            by='Confidence',
            ascending=False,
            inplace=False)
        d = df[['Consequent', 'Confidence']].reset_index(drop=True).head(2).iloc[0:, 0][0].replace('{', '').replace('}',
                                                                                                                    '').replace(
            '\'', '')
        st.dataframe(df[['Consequent', 'Confidence']].reset_index(drop=True).head(5))
        query = f'''
        select bt.book_id,book.persian_title
        from book
        inner join book_tag bt on book.id = bt.book_id
        inner join tag on bt.tag_id = tag.tag_id
        inner join book_writer on book.id = book_writer.book_id
        inner join publisher on book.publisher_id = publisher.id
        where tag_title like '%{d}%' or tag_title like '%{li1[0]}%' and rate between 0 and 5
        order by rate DESC
        limit 10
                
        '''
        data = run_query(query)
        dff = pd.DataFrame(data, columns=['book_id', 'title'])
        st.dataframe(dff.reset_index(drop=True))


def q17():
    # Average Rate for Each Tag Title
    st.subheader("Average Rate for Each Tag Title")
    query11 = """
        SELECT t.tag_title AS tag, AVG(b.rate) AS avg_rate
        FROM book_tag AS bt
        JOIN tag AS t ON bt.tag_id = t.tag_id
        JOIN book AS b ON bt.book_id = b.id
        GROUP BY tag
        """
    mycursor = mydb.cursor()
    mycursor.execute(query11)
    data = mycursor.fetchall()
    column_names = [out[0] for out in mycursor.description]
    df3 = pd.DataFrame(data, columns=column_names)
    chart3 = alt.Chart(df3).mark_area(
        color="lightblue",
        interpolate='step-after',
        line=True
    ).encode(
        x='tag',
        y='avg_rate'
    ).interactive()
    st.altair_chart(chart3, use_container_width=True)
    tags = df3['tag'].unique().tolist()
    tag_input = st.text_input("Enter Tags (separated by comma) or 'random'", "")
    if tag_input.lower() == "random":
        selected_tags = random.sample(tags, 10)
    else:
        selected_tags = [tag.strip() for tag in tag_input.split(",")]
    filtered_df = df3[df3['tag'].isin(selected_tags)]
    chart = alt.Chart(filtered_df).mark_area(
        color="lightblue",
        interpolate='step-after',
        line=True
    ).encode(
        x='tag',
        y='avg_rate'
    ).interactive()
    st.title("Average Rate for Selected Tags")
    st.altair_chart(chart, use_container_width=True)


def q18():
    # Price Distribution of Top Ten Publishers
    st.subheader("Price Distribution of Top Ten Publishers")
    query = """
       SELECT publisher_name, price
       FROM book
       WHERE publisher_name != ''
       ORDER BY price DESC
       LIMIT 10
       """
    data = run_query(query)
    df = pd.DataFrame(data, columns=["Publisher", "Price"])
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Price:Q", bin=alt.Bin(maxbins=20), title="Price"),
        y=alt.Y("count():Q", title="Count"),
        color=alt.Color("Publisher:N", legend=alt.Legend(title="Publisher"))
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)


def q19():
    # More options Word Cloud
    st.subheader("More options : Word Cloud")
    query = '''SELECT tag_title FROM tag;'''
    data = run_query(query)
    genre_list = []
    for i in data:
        genre_list.append(i[0])
    li1 = st.multiselect(
        "Select your tag:",
        genre_list, max_selections=1)
    if len(li1) > 0:
        mycursor = mydb.cursor()
        mycursor.execute(f'''
                            SELECT tag_title,content
                            FROM book
                            inner join book_description on book.id = book_description.book_id
                            inner join book_tag on book.id = book_tag.book_id
                            inner join tag on book_tag.tag_id = tag.tag_id
                            where tag_title in (%s) 
                ''', tuple(li1))
        data = mycursor.fetchall()
        df = pd.DataFrame(data, columns=['tag_title', 'content'])
        text = " ".join(review for review in df.content)
        if text:
            text = text.lower()
            number_pattern = r'\d+'
            text = re.sub(pattern=number_pattern, repl=" ", string=text)
            text = text.translate(str.maketrans('', '', string.punctuation))
            with open('stopwords.txt', encoding='utf-8') as stopwords_file:
                stopwords = stopwords_file.readlines()
                stopwords_file.close()
            stopwords = [line.replace('\n', '') for line in stopwords]
            stopwords.extend(hazm.stopwords_list())
            stopwords.append('no')
            stopwords.append('description')
            stopwords.append('کتاب')
            stopwords.append('کتابی')
            stopwords.append('رمان')
            stopwords.append('داستان')
            stopwords.append(li1[0])
            stopwords = set(stopwords)
            mask_array = np.array(Image.open("image.jpg"))
            wordcloud = WordCloudFa(stopwords=stopwords, background_color="white", width=900, height=500,
                                    persian_normalize=True, include_numbers=False, no_reshape=False,
                                    collocations=False).generate(text)
            fig, ax = plt.subplots(figsize=(24, 12))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.write(fig)


def q20():
    st.subheader("Tell me about your feelings and I will tell you what genre of book to read")
    t = st.text_input('')
    rco = (gettr(t))
    f'{rco}'


try:
    page_options = {
        "chart 1": q1,
        "chart 2": q2,
        "chart 3": q3,
        "chart 4": q4,
        "chart 5": q5,
        "chart 6": q6,
        "chart 7": q7,
        "chart 8": q8,
        "chart 9": q9,
        "Interactive chart": q10,
        "Buyer request 1": q11,
        "Buyer request 2": q12,
        "Author request": q13,
        "hypothesis test": q14,
        "More options graph": q15,
        "More options Correlation": q16,
        "More options Average Rate": q17,
        "More options Price Distribution": q18,
        "More options Word Cloud": q19,
    }
    selected_page = st.sidebar.selectbox("select:", list(page_options.keys()))
    page_options[selected_page]()
except mysql.connector.Error as err:
    st.error(f"An error occurred: {err}")

if mydb.is_connected():
    mydb.close()
