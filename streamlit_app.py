import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Set up Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the smoothie
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on Smoothie will be:', name_on_order)

# Fetch the fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Create a multiselect widget for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

ingredients_string = ''
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + 'Nutrition Information')
        
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" +fruit_chosen)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)


    # Remove any trailing space from the ingredients_string
    ingredients_string = ingredients_string.strip()

    # SQL insert statement with direct string formatting
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Display the submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            # Execute the insert statement
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error placing the order: {e}")
