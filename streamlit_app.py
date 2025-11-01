# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Streamlit title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
fruit_list = [row[0] for row in my_dataframe.collect()]  # Convert to Python list

# Fruit selector
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Show fruit nutrition info via API
if ingredients_list:
    st.subheader("🍎 Nutrition Information for Your Selected Fruits")
    for fruit_chosen in ingredients_list:
        url = f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame([data])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"⚠️ Could not fetch info for {fruit_chosen}")

    # Insert smoothie order
    ingredients_string = ', '.join(ingredients_list)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
