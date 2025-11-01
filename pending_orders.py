# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Title
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")

st.write("Orders that need to be filled.")

# Get active Snowflake session
session = get_active_session()

# Get only orders where ORDER_FILLED = FALSE
my_dataframe = (
    session.table("smoothies.public.orders")
    .filter(col("ORDER_FILLED") == False)
    .select(
        col("ORDER_UID"),
        col("NAME_ON_ORDER"),
        col("ORDER_FILLED"),
        col("INGREDIENTS").cast("string").alias("INGREDIENTS")
    )
    .to_pandas()
)

# Only show table if data exists
if not my_dataframe.empty:
    editable_df = st.data_editor(my_dataframe, use_container_width=True)

    submitted = st.button("Submit")
    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)

        try:
            og_dataset.merge(
                edited_dataset,
                (og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"]),
                [when_matched().update({"ORDER_FILLED": edited_dataset["ORDER_FILLED"]})],
            )
            st.success("✅ Orders Updated!", icon="👍")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
else:
    st.success("👍 There are no pending orders right now")
