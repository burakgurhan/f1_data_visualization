import streamlit as st
import pandas as pd
from data_processing import load_session_data
from data_processing import GetDataframes
from visualization import *
from constants import drivers, teams
from urllib.request import urlopen
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# Load calendar to get locations
calendar_df = GetDataframes.load_calendar()
location_list = calendar_df["circuit_short_name"].values
st.title("Formula 1 Data Visualization")

location = st.sidebar.selectbox(label="Select the race location.", options=location_list, placeholder="Choose a race")

# Load all dataframes
df, session_key = load_session_data(location)   
driver_df, team_colors = GetDataframes.drivers_dataframe(session_key=session_key)    # Driver and team informaitons
lap_times_df = GetDataframes.lap_times_df(df, driver_df)
positions_df = GetDataframes.positions_dataframe(session_key, driver_df)
fastest_lap = GetDataframes.fastest_lap_df(lap_times_df)
top_10_df = GetDataframes.top_10_dataframe(positions_df, driver_df)





st.write("Session Information:")

# 1. Top 10 Finishers
st.header("Race Results")
st.subheader("Top 10 Finishers")
barplot = plot_top10(top_10_df, location)
st.plotly_chart(barplot)


# 2. Race Results
st.subheader("Positions")
st.dataframe(positions_df[10:], hide_index=True)


# 3. Fastest Lap
st.subheader("Fastest Lap")
st.dataframe(fastest_lap)


# 5. Heatmap
st.header("Heatmap of Lap Times")
heatmap = plot_heatmap_of_laptimes(lap_times_df)
st.plotly_chart(heatmap)


# 6. Line Graph for Lap times of Drivers 
st.header("Line Graph for Lap times of Drivers")
lineplot = line_plot_of_laptimes(lap_times_df,top_10_df)
st.plotly_chart(lineplot)


# 7. Box Plot for Lap times of Drivers
st.header("Box Plot of Lap times of Drivers")
boxplot = box_plot_laptimes(lap_times_df)
st.plotly_chart(boxplot)


# 8. Driver Comparision
st.subheader("Driver Comparisions")
driver_comparision_df = GetDataframes.get_driver_performance(lap_times_df, driver_df)
st.dataframe(driver_comparision_df, hide_index=True)


# 9. Performance of the Teams
st.header("Performance of the Teams")
team_performance_df = GetDataframes.get_teams_performance(driver_comparision_df)
team_performance = plot_team_performance(team_performance_df, team_colors)
st.plotly_chart(team_performance)


# 4. Lap times of All Drivers
st.header("Lap Times of Drivers")
st.dataframe(lap_times_df)


