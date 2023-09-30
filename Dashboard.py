import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
import altair as alt

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

def run_query(query):
    try:
        mycursor = mydb.cursor()
        mycursor.execute(query)
        data = mycursor.fetchall()
        return data
    except mysql.connector.Error as err:
        st.error(f"Error executing the query: {err}")
        return None
def page1():
    st.title("Analytical charts")

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

try:
    page_options = {
        "Analytical charts": page1
    }
    selected_page = st.sidebar.selectbox("Select a page", list(page_options.keys()))
    page_options[selected_page]()
except mysql.connector.Error as err:
    st.error(f"An error occurred: {err}")

if mydb.is_connected():
    mydb.close()