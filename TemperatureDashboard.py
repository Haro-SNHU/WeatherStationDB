import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from TemperatureDB import TemperatureReadings

# Database Settings
DB_USERNAME = os.getenv("db_username")
DB_PASSWORD = os.getenv("db_password")
temperature_readings = TemperatureReadings(DB_USERNAME, DB_PASSWORD)

projection = {'_id': False}
temperature = pd.DataFrame.from_records(temperature_readings.read({}, projection)) 

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe."""
    st.title("WeatherPi")
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection

selection = aggrid_interactive_table(temperature)

if selection:
    st.write("You selected:")
    st.json(selection["selected_rows"])