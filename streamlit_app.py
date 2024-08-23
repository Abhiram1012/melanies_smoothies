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
    for fruit_chosen in ingredients_list:
        ingredients_string += f"{fruit_chosen} "  # Add a space after each fruit

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        st.subheader(f'{fruit_chosen} Nutrition Information')

        # Fetch nutrition information from Fruityvice API
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
        if fruityvice_response.status_code == 200:
            fv_data = fruityvice_response.json()
            st.dataframe(pd.json_normalize(fv_data), use_container_width=True)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}. Please try again later.")

    # Remove any trailing space from the ingredients_string
    ingredients_string = ingredients_string.strip()

    # SQL insert statement with parameterized query
    my_insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (%s, %s)
    """

    # Display the submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        try:
            # Execute the insert statement with parameters
            session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        except Exception as e:
            st.error(f"Error placing the order: {e}")
