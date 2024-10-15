import streamlit as st
import pandas as pd
from data_processing import load_session_data, get_unique_lap_numbers, get_unique_driver_numbers, create_lap_times_df
from visualization import plot_heatmap_of_laptimes, line_plot_of_laptimes, box_plot_laptimes
from constants import drivers, teams

st.title("F1 Race Data Graphs")

country = st.text_input("Enter the country of the race", "Belgium")
df = load_session_data(country)

st.write("Session Information:")


# Example DataFrame creation
lap_numbers = list(df.lap_number.unique())
driver_numbers = list(df.driver_number.unique())

lap_times_df = create_lap_times_df(df, lap_numbers, driver_numbers)

st.write("Lap Times DataFrame:")
st.dataframe(lap_times_df)

# First viz as heatmap
heatmap = plot_heatmap_of_laptimes(lap_times_df)
st.plotly_chart(heatmap)

# Second viz as lineplot
lineplot = line_plot_of_laptimes(lap_times_df)
st.plotly_chart(lineplot)

# Third viz as boxplot
boxplot = box_plot_laptimes(lap_times_df)
st.plotly_chart(boxplot)