import pandas as pd
import mysql.connector
import scipy.stats as stats
from mysql.connector import Error
db_config = {
    'host': '****',
    'database': '****',
    'user': '****',
    'password': '****'
}
try:
    connection = mysql.connector.connect(**db_config)
    query = "SELECT * FROM book"
    data = pd.read_sql_query(query, connection)
    hardcover_data = data[data['cover_type'] == 'جلد سخت']
    softcover_data = data[data['cover_type'] == 'شومیز']

    t_stat, p_value = stats.ttest_ind(hardcover_data['price'], softcover_data['price'])
    print('t_stat =', t_stat)
    print('p_value =', p_value)

    if p_value < 0.05:
        print("There is a significant difference in their prices." )
    else:
        print("There is no significant difference in their prices.")

except Error as e:
    print(f"Database connection error: {e}")

finally:
    if connection.is_connected():
        connection.close()