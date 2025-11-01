# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie")

# Input name
name_on_order = st.text_input("Name on Smoothie:")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#fruit_options = [row['FRUIT_NAME'] for row in my_dataframe.collect()]  # convert to list

# Multiselect for ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Only proceed if fruits are selected
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
            if response.status_code == 200:
                data = response.json()
                st.dataframe(data=data, use_container_width=True)
            else:
                st.error(f"Sorry, {fruit_chosen} is not in our database.")
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

    # Submit button for saving the order
    if st.button("Submit Order"):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
