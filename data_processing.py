import json
import pandas as pd
from constants import team_colors
from urllib.request import urlopen
from visualization import get_boundaries

class GetDataframes:
    def __init__(self):
        self.base_url = 'https://api.openf1.org/v1/'
        self.get_boundaries = get_boundaries


    def load_calendar(self):
        response = urlopen(f'{self.base_url}meetings?year=2024')
        calendar_data = json.loads(response.read().decode('utf-8'))
        return pd.DataFrame(calendar_data)
    

    def get_country_names(self, year):
        try:
            response = urlopen(f'{self.base_url}meetings?year={year}')
            data = json.loads(response.read().decode('utf-8'))
            country_names = [item["country_name"] for item in data]
            meeting_names = [item["meeting_name"] for item in data]
            display_names = [f"{country_name} - {meeting_name}" for country_name, meeting_name in zip(country_names, meeting_names)]
            return country_names, meeting_names, display_names
        except Exception as e:
            print(f"Error: {e}")
            return [], [], []
    

    def drivers_dataframe(self, session_key):
        try:
            response = urlopen(f'{self.base_url}drivers?session_key={session_key}')
            driver_data = json.loads(response.read().decode('utf-8'))
            driver_df = pd.DataFrame(driver_data)
            driver_numbers = list(driver_df["driver_number"].unique())
            driver_df["full_name"] = driver_df["first_name"] + " " + driver_df["last_name"]
            driver_df["driver_colour"] = driver_df["team_name"].map(team_colors)
            driver_df = driver_df[["country_code", "full_name", "driver_number", "team_name", "name_acronym", "driver_colour"]].copy()
            driver_dict = driver_df.to_dict(orient="records")
            return driver_df, team_colors, driver_dict
        except Exception as e:
            print(f"Error: {e}")
            return [], [], []
    

    def positions_dataframe(self, session_key, driver_df):
        try:
            response = urlopen(f'{self.base_url}position?session_key={session_key}')
            position_data = json.loads(response.read().decode('utf-8'))
            position_df = pd.DataFrame(position_data)
            position_df = position_df.groupby("position")["driver_number"].last().reset_index()
            position_df["Driver"] = [driver_df[driver_df["driver_number"]==x]["full_name"].values[0] for x in position_df['driver_number'].values]
            position_df["Team"] = [driver_df[driver_df["driver_number"]==x]["team_name"].values[0] for x in position_df['driver_number'].values]
            position_df.columns = ["Result" , "Driver Number", "Driver", "Team"]
            return position_df
        except Exception as e:
            print(f"Error: {e}")
            return []

    @staticmethod
    def fastest_lap_df(lap_times_df, driver_df):
        try:
            fastest_lap_df = lap_times_df.min().sort_values().reset_index(name="Fastest Lap")
            fastest_lap_df.columns = ["Driver Acronym", "Fastest Lap"]
            fastest_lap_df["Driver Name"] = [driver_df[driver_df["name_acronym"]==x]["full_name"].values for x in fastest_lap_df["Driver Acronym"].values]
            fastest_lap = fastest_lap_df.iloc[0]
            fastest_lap = fastest_lap.to_dict()
            return fastest_lap_df.iloc[:5], fastest_lap
        except Exception as e:
            print(f"Error: {e}")
            return [], []
    
    @staticmethod
    def top_10_dataframe(position_df, driver_df):
        try:
            points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            top_10_finish = position_df[:10]
            top_10_finish_df = pd.DataFrame({"Driver Number":top_10_finish["Driver Number"], "Points":points})
            top_10_finish_df["Driver"] = [driver_df[driver_df["driver_number"]==x]["name_acronym"].values[0] for x in top_10_finish_df["Driver Number"].values]
            top_10_finish_df["Driver Colour"] = [driver_df[driver_df["driver_number"]==x]["driver_colour"].values[0] for x in top_10_finish_df["Driver Number"].values]
            podium_df = position_df.iloc[:3]
            podium = podium_df.to_dict(orient="records")
            top_10_dict=top_10_finish_df.to_dict(orient="records")
            return top_10_finish_df, podium, top_10_dict
        except Exception as e:
            print(f"Error: {e}")
            return [], [], []

    @staticmethod
    def lap_times_df(df: pd.DataFrame, driver_df: pd.DataFrame):
        try:
            lap_numbers = list(df.lap_number.unique())
            driver_numbers = list(df.driver_number.unique())

            lap_times_df = pd.DataFrame(index=lap_numbers, columns=driver_numbers)

            for index, row in df.iterrows():
                lap_number = row["lap_number"]
                driver_number = row["driver_number"]
                lap_duration = row["lap_duration"]

                lap_times_df.loc[lap_number, driver_number] = lap_duration

            lap_times_df = lap_times_df.astype(float)
        except Exception as e:
            print(f"Error: {e}")
        try:
            lap_times_df.columns = lap_times_df.columns.map(dict(zip(driver_df["driver_number"].values, driver_df["name_acronym"].values)))
        except ValueError as v:
            print(f"Error: {v}")
        lap_times_df.bfill(inplace=True)
        return lap_times_df
    
    @staticmethod
    def get_driver_performance(self, lap_times_df, driver_df):
        try:
            lower_bound, upper_bound = self.get_boundaries(lap_times_df)
            lap_times_df = lap_times_df[(lap_times_df<upper_bound.median())&(lap_times_df>lower_bound.median())]
            lap_times_df = lap_times_df.astype(float)
            min_lap_times = lap_times_df.min().rename("Fastest Lap of Drivers")
            avg_lap_times = lap_times_df.mean().rename("Average Lap Times of Drivers")

            driver_comparision_df = pd.merge(min_lap_times, avg_lap_times, on=min_lap_times.index)
            driver_comparision_df["Teams"] = [driver_df[driver_df['name_acronym']==x]["team_name"].values[0] for x in driver_comparision_df["key_0"]]
            driver_comparision_df.rename(columns={"key_0":"Driver"})
            driver_comparision_df.sort_values(by="Fastest Lap of Drivers", inplace=True)
            return driver_comparision_df
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    @staticmethod
    def get_teams_performance(driver_comparision_df):
        try:
            avg_team_times_df = driver_comparision_df.groupby("Teams")["Average Lap Times of Drivers"].mean().rename({"Average Lap Times of Drivers":"Average Lap Times of Teams"}).sort_values()
            avg_team_times_df = avg_team_times_df.reset_index(name="Average Lap Times of Teams")
            avg_team_times_df["Team Differences"] = avg_team_times_df["Average Lap Times of Teams"] - avg_team_times_df["Average Lap Times of Teams"].min()
            return avg_team_times_df
        except Exception as e:
            print(f"Error: {e}")
            return []

    @staticmethod
    def get_speed_trap_df(df: pd.DataFrame, driver_df: pd.DataFrame):
        try:
            lap_numbers = list(df.lap_number.unique())
            driver_numbers = list(df.driver_number.unique())
            speed_trap_df = pd.DataFrame(index=lap_numbers, columns=driver_numbers)
            for index, row in df.iterrows():
                lap_number = row["lap_number"]
                driver_number = row["driver_number"]
                speed_trap = row["st_speed"]
                speed_trap_df.loc[lap_number, driver_number] = speed_trap
        except Exception as e:
            print(f"Error: {e}")
        
        try:
            speed_trap_df.columns = speed_trap_df.columns.map(dict(zip(driver_df["driver_number"].values, driver_df["name_acronym"].values)))
        except ValueError as v:
            print(f"Error: {v}")
        fastest_in_speed_trap = speed_trap_df.max().reset_index(name="Speed Trap Value").sort_values(by="Speed Trap Value", ascending=False).iloc[0]
        fastest_in_speed_trap = fastest_in_speed_trap.to_dict()
        return speed_trap_df, fastest_in_speed_trap
    

    def get_pit_intervals(self, session_key, driver_df):
        try:
            response = urlopen(f'{self.base_url}pit?session_key={session_key}&pit_duration<40')
            pit_data = json.loads(response.read().decode('utf-8'))
            fastest_pit_stop = pd.DataFrame(pit_data)
            fastest_pit_stop = fastest_pit_stop.sort_values(by="pit_duration").head(1)
            # Convert driver_number to a list
            fastest_pit_stop["driver_name"] = fastest_pit_stop["driver_number"].apply(
                lambda x: driver_df[driver_df["driver_number"] == int(x)]["full_name"].values[0]
            )

            fastest_pit_stop["team_name"] = fastest_pit_stop["driver_number"].apply(
                lambda x: driver_df[driver_df["driver_number"] == int(x)]["team_name"].values[0]
            )

            fastest_pit_stop_dict = fastest_pit_stop.to_dict(orient="records")
            return fastest_pit_stop_dict
        except Exception as e:
            print(f"Error: {e}")
            return []

def load_session_data(country, year):
    try:
        response = urlopen(f'https://api.openf1.org/v1/sessions?country_name={country}&session_name=Race&year={year}')
        session_info = json.loads(response.read().decode('utf-8'))
        
        if not session_info:
            return None, None, None
            
        session_key = session_info[0]["session_key"]
        circuit_name = session_info[0]["circuit_short_name"]

        response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}')
        laps_data = json.loads(response.read().decode('utf-8'))

        df = pd.DataFrame(data=laps_data)
        return df, session_key, circuit_name
        
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None
