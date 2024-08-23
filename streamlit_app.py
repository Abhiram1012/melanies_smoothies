import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Establish Snowflake connection
cnx = st.experimental_connection("snowflake")
session = cnx.session()

# Create orders using Streamlit inputs
if st.button('Create Orders'):
    # Create order for Kevin
    session.sql("""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('Apples, Lime, Ximenia', 'Kevin', FALSE)
    """).collect()
    
    # Create order for Divya
    session.sql("""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('Dragon Fruit, Guava, Figs, Jackfruit, Blueberries', 'Divya', TRUE)
    """).collect()
    
    # Create order for Xi
    session.sql("""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('Vanilla Fruit, Nectarine', 'Xi', TRUE)
    """).collect()
    
    st.success('Orders created successfully!')
