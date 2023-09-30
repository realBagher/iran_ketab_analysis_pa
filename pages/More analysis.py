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


'# Correlation between book tags'
rules_df=pd.read_csv('Confidence.csv')
t=rules_df.loc[(rules_df.len_act>=1)&(rules_df.len_cqt==1)][['cqt']].drop_duplicates().values
tag_l=[x[0] for x in t]
li1=st.multiselect(
    "Select your tag:",
    tag_l,max_selections=3)
txt=' '.join([x for x in li1])
if len(li1)>0:
    df = rules_df.loc[(rules_df.len_act == len(li1)) & (rules_df.act.str.contains(txt))].sort_values(by='Confidence',
                                                                                                  ascending=False,
                                                                                                  inplace=False)
    st.dataframe(df[['Consequent','Confidence']].head(5))


