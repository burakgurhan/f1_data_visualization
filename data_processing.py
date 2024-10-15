import pandas as pd
import json
from urllib.request import urlopen
from constants import drivers, teams

def load_session_data(country):
    # API Connection
    response = urlopen(f'https://api.openf1.org/v1/sessions?country_name={country}&session_name=Race&year=2024')
    # Get session_key to access details of the race.
    session_info = json.loads(response.read().decode('utf-8'))
    # Get session key.
    session_key = session_info[0]["session_key"]

    # Query for race.
    response = urlopen(f'https://api.openf1.org/v1/laps?session_key={session_key}')
    # Get data from response.
    data = json.loads(response.read().decode('utf-8'))

    df = pd.DataFrame(data=data)
    return df

def get_unique_lap_numbers(df):
    return list(df.lap_number.unique())

def get_unique_driver_numbers(df):
    return list(df.driver_number.unique())

def create_lap_times_df(df, lap_numbers, driver_numbers):
    lap_times_df = pd.DataFrame(index=lap_numbers, columns=driver_numbers)


    for index, row in df.iterrows():
        lap_number = row['lap_number']
        driver_number = row['driver_number']
        lap_times_df.at[lap_number, driver_number] = row['lap_duration']
    
    lap_times_df = lap_times_df.astype(float)
    lap_times_df.columns = lap_times_df.columns.map(drivers)
    lap_times_df.fillna(lap_times_df.mean(), inplace=True)
    return lap_times_df