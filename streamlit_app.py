import streamlit as st
from data_processing import load_session_data
from data_processing import GetDataframes
from visualization import *
from urllib.request import urlopen
import json
import urllib
from groq_integration import Summary

st.title("Formula 1 Data Visualization")

# Sidebar
year = st.sidebar.select_box("Select Year", [2023, 2024, 2025], index=1)

## Get Country and Meeting Names
def get_country_names(year):
    response = urlopen(f'https://api.openf1.org/v1/meetings?year={year}')
    data = json.loads(response.read().decode('utf-8'))
    country_names = [item["country_name"] for item in data]
    meeting_names = [item["meeting_name"] for item in data]
    display_names = [f"{country_name} - {meeting_name}" for country_name, meeting_name in zip(country_names, meeting_names)]
    return country_names, meeting_names, display_names

country_names, meeting_names, display_names = get_country_names(year)
selected_race_name = st.sidebar.selectbox("Select Race", display_names, index=0)
selected_country_name = selected_race_name.split(" - ")[0]
selected_meeting_name = selected_race_name.split(" - ")[1]
encoded_country_name = urllib.parse.quote(selected_country_name)

# Load all dataframes
df, session_key = load_session_data(encoded_country_name, year)   
driver_df, team_colors = GetDataframes.drivers_dataframe(session_key=session_key)    # Driver and team informaitons
lap_times_df = GetDataframes.lap_times_df(df, driver_df)
positions_df = GetDataframes.positions_dataframe(session_key, driver_df)
fastest_lap = GetDataframes.fastest_lap_df(lap_times_df)
top_10_df = GetDataframes.top_10_dataframe(positions_df, driver_df)
speed_trap_df = GetDataframes.get_speed_trap_df(df, driver_df)



# 1. Top 10 Finishers
st.header("Race Results")
st.subheader("Top 10 Finishers")
barplot = plot_top10(top_10_df, selected_meeting_name)
st.plotly_chart(barplot)


# 2. Race Results
st.subheader("Positions")
st.dataframe(positions_df[10:], hide_index=True)


# 3. Fastest Lap
st.subheader("Fastest Lap")
st.write(f"The fastest lap of the race is {fastest_lap.iloc[0].values[1]} succeded by {fastest_lap.iloc[0].values[0]}.")
st.dataframe(fastest_lap, use_container_width=False, hide_index=True)


# 4. AI Race Summary
summary_gen = Summary(
    year, country_names, lap_times_df, fastest_lap, top_10_df, speed_trap_df, driver_df
)
race_summary = summary_gen.create_summary()
st.header("AI Race Summary")
st.write(race_summary)


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



# 10. Speed Trap 
st.header("Speed Trap")
st.dataframe(speed_trap_df.max().reset_index(name="Max in Speed Trap"), hide_index=True, use_container_width=False)
# 11. Lap times of All Drivers
st.header("Lap Times of Drivers")
st.dataframe(lap_times_df)


