import json
import urllib
import streamlit as st
from urllib.request import urlopen
from data_processing import load_session_data
from data_processing import GetDataframes
from visualization import *
from groq_integration import create_race_summary

st.title("Formula 1 Data Visualization")

# Sidebar
year = st.sidebar.selectbox("Select Year", [2023, 2024, 2025], index=1)

country_names, meeting_names, display_names = GetDataframes.get_country_names(year)
selected_race_name = st.sidebar.selectbox("Select Race", display_names, index=0)
selected_country_name = selected_race_name.split(" - ")[0]
selected_meeting_name = selected_race_name.split(" - ")[1]
encoded_country_name = urllib.parse.quote(selected_country_name)

# Load all dataframes
df, session_key, circuit_name = load_session_data(encoded_country_name, year)   
driver_df, team_colors, driver_dict = GetDataframes.drivers_dataframe(session_key=session_key)    # Driver and team informaitons
lap_times_df = GetDataframes.lap_times_df(df, driver_df)
position_df = GetDataframes.positions_dataframe(session_key, driver_df)
fastest_lap_df, fastest_lap = GetDataframes.fastest_lap_df(lap_times_df, driver_df)
top_10_df, podium, top_10 = GetDataframes.top_10_dataframe(position_df, driver_df)
speed_trap_df, fastest_in_speed_trap = GetDataframes.get_speed_trap_df(df, driver_df)
fastest_pit_stop_dict = GetDataframes.get_pit_intervals(session_key, driver_df)

# Create race_info dictionary
race_info = {}
race_info["Year"] = year
race_info["Country"] = selected_country_name
race_info["Meeting Name"] = selected_meeting_name
race_info["Circuit"] = circuit_name


# 1. AI Race Summary
race_summary = create_race_summary(
    race_info,
    driver_dict,
    podium,
    top_10,
    fastest_lap,
    fastest_in_speed_trap,
    fastest_pit_stop_dict
)
st.header("AI Race Summary")
st.write(race_summary)


# 2. Top 10 Finishers
st.header("Race Results")
st.subheader("Top 10 Finishers")
barplot = plot_top10(top_10_df, selected_meeting_name)
st.plotly_chart(barplot)


# 3. Race Results
st.subheader("Positions")
st.dataframe(position_df[10:], hide_index=True)


# 4. Fastest Lap
st.subheader("Fastest Lap")
st.write(f"The fastest lap of the race is {fastest_lap_df.iloc[0].values[1]} succeded by {fastest_lap_df.iloc[0].values[0]}.")
st.dataframe(fastest_lap_df, use_container_width=False, hide_index=True)


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
st.write("Derived from the average lap times of the drivers of each team.")
team_performance_df = GetDataframes.get_teams_performance(driver_comparision_df)
team_performance = plot_team_performance(team_performance_df, team_colors)
st.plotly_chart(team_performance)


# 10. Speed Trap 
st.header("Speed Trap")
st.dataframe(speed_trap_df.max().reset_index(name="Max in Speed Trap"), hide_index=True, use_container_width=False)

# 11. Lap times of All Drivers
st.header("Lap Times of Drivers")
st.dataframe(lap_times_df)