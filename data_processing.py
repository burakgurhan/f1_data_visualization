import pandas as pd
import json
from urllib.request import urlopen
from constants import drivers, teams


class GetDataframes:
    def load_calendar():
        response = urlopen(f'https://api.openf1.org/v1/meetings?year=2024')
        calendar_data = json.loads(response.read().decode('utf-8'))
        return pd.DataFrame(calendar_data)
    
    def drivers_dataframe(session_key):
        response = urlopen(f'https://api.openf1.org/v1/drivers?session_key={session_key}')
        driver_data = json.loads(response.read().decode('utf-8'))
        driver_df = pd.DataFrame(driver_data)
        driver_numbers = list(driver_df["driver_number"].unique())
        driver_df["full_name"] = driver_df["first_name"] + " " + driver_df["last_name"]

        team_colors = {'Red Bull Racing': 'cornflowerblue',
        'Williams': 'lightblue',
        'RB': 'lightpink',
        'McLaren': 'orange',
        'Alpine': 'darkblue',
        'Aston Martin': 'green',
        'Ferrari': 'red',
        'Haas F1 Team': 'white',
        'Kick Sauber': 'lightgreen',
        'Mercedes': 'silver'}

        driver_df["driver_colour"] = driver_df["team_name"].map(team_colors)

        return driver_df, team_colors
    

    def positions_dataframe(session_key, driver_df):
        response = urlopen(f'https://api.openf1.org/v1/position?session_key={session_key}')
        position_data = json.loads(response.read().decode('utf-8'))
        position_df = pd.DataFrame(position_data)
        position_df = position_df.groupby("position")["driver_number"].last().reset_index()
        position_df["Driver"] = [driver_df[driver_df["driver_number"]==x]["full_name"].values[0] for x in position_df['driver_number'].values]
        position_df.columns = ["Result" , "Driver Number", "Driver"]
        return position_df

    def fastest_lap_df(lap_times_df):
        fastest_lap_df = lap_times_df.min().sort_values().reset_index(name="Fastest Lap")
        fastest_lap_df.columns = ["Driver Acronym", "Fastest Lap"]
        return fastest_lap_df.iloc[0]
    
    def top_10_dataframe(position_df, driver_df):
        points = [25,18,15,12,10,8,6,4,2,1]
        top_10_finish = position_df[:10]
        top_10_finish_df = pd.DataFrame({"Driver Number":top_10_finish["Driver Number"], "Points":points})
        top_10_finish_df["Driver"] = [driver_df[driver_df["driver_number"]==x]["name_acronym"].values[0] for x in top_10_finish_df["Driver Number"].values]
        top_10_finish_df["Driver Colour"] = [driver_df[driver_df["driver_number"]==x]["driver_colour"].values[0] for x in top_10_finish_df["Driver Number"].values]
        return top_10_finish_df

    def lap_times_df(df, driver_df):
        lap_numbers = list(df.lap_number.unique())
        driver_numbers = list(df.driver_number.unique())

        lap_times_df = pd.DataFrame(index=lap_numbers, columns=driver_numbers)

        for index, row in df.iterrows():
            lap_number = row["lap_number"]
            driver_number = row["driver_number"]
            lap_duration = row["lap_duration"]

            lap_times_df.loc[lap_number, driver_number] = lap_duration

        lap_times_df = lap_times_df.astype(float)
        lap_times_df.columns = driver_df["name_acronym"]
        return lap_times_df

    def get_driver_performance(lap_times_df, driver_df):
        min_lap_times = lap_times_df.min().rename("Fastest Lap of Drivers")
        avg_lap_times = lap_times_df.mean().rename("Average Lap Times of Drivers")

        driver_comparision_df = pd.merge(min_lap_times, avg_lap_times, on=min_lap_times.index)
        driver_comparision_df["Teams"] = [driver_df[driver_df['name_acronym']==x]["team_name"].values[0] for x in driver_comparision_df["key_0"]]
        driver_comparision_df.rename(columns={"key_0":"Driver"})
        driver_comparision_df.sort_values(by="Fastest Lap of Drivers", inplace=True)
        return driver_comparision_df
    
    def get_teams_performance(driver_comparision_df):
        avg_team_times_df = driver_comparision_df.groupby("Teams")["Average Lap Times of Drivers"].mean().rename({"Average Lap Times of Drivers":"Average Lap Times of Teams"}).sort_values()

        avg_team_times_df = avg_team_times_df.reset_index(name="Average Lap Times of Teams")
        avg_team_times_df["Team Differences"] = avg_team_times_df["Average Lap Times of Teams"] - avg_team_times_df["Average Lap Times of Teams"].min()
        return avg_team_times_df



def load_session_data(country):
    # API Connection
    response = urlopen(f'https://api.openf1.org/v1/sessions?circuit_short_name={country}&session_name=Race&year=2024')
    # Get session_key to access details of the race.
    session_info = json.loads(response.read().decode('utf-8'))
    # Get session key.
    session_key = session_info[0]["session_key"]

    # Query for race.
    response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}')
    # Get data from response.
    data = json.loads(response.read().decode('utf-8'))

    df = pd.DataFrame(data=data)

    return df, session_key
