"""Functions for loading weather data from Dark Sky."""
import numpy as np
import pandas as pd
import csv
from darksky import forecast
from datetime import datetime as dt


def get_precinct_centroids(precinct_dict):
    """Get the centroid for each precinct."""
    return {
        k: {
            'latitude': v['shape_gps'].centroid.y,
            'longitude': v['shape_gps'].centroid.x
        }
        for k, v in precinct_dict.items()
    }


def get_mean_latlon(centroids):
    """Get the mean of all the centroids for each district."""
    arr = [[v['latitude'], v['longitude']] for v in centroids.values()]
    return np.mean(arr, axis=0)


def read_api_key(keyfile='../precrime_data/darksky_api_key'):
    """Read the file containing the Dark Sky API key."""
    with open(keyfile, 'r') as f:
        key = f.read().replace('\n', '')
    return key


def write_weather_data(dates,
                       hours,
                       apikey,
                       latlon,
                       append_output=False,
                       filepath='../precrime_data/weather_hist.csv'):
    """Call the Dark Sky API and save the weather data.

    Parameters
    ----------
    dates : list
        A list of dates (supporting .year, .month, and .day) to
        download the weather for
    hours : list
        A list of integers representing the hours of each day
        that we want to get the weather for. The total number of forecasts
        download is len(dates) * len(hours)
    apikey : string
        Dark Sky API key
    latlon : tuple
        latlon[0] = latitude, latlon[1] = longitude
    append_output : boolean, optional, default False
        If True, will not write a header row and will not overwrite the file
    filepath : string, optional
        Where to write the output

    Returns
    -------
    None
    """
    if append_output:
        write_header = False
        file_mode = 'a'
    else:
        write_header = True
        file_mode = 'w'
    weather_location = [apikey, latlon[0], latlon[1]]
    with open(filepath, file_mode, newline='') as csvfile:
        # Create the list of dict fields we'll be including in the file.
        # Add 'precipType' in case it isn't currently raining while
        # this script is being run.
        with forecast(*weather_location) as current_weather:
            weather_fields = sorted(list(set(
                ['precipType'] +
                list(current_weather.currently._data.keys())
            )))

        writer = csv.DictWriter(csvfile, fieldnames=weather_fields)
        if write_header:
            writer.writeheader()
        for date in dates:
            for hour in hours:
                t = dt(date.year, date.month, date.day, hour).isoformat()
                with forecast(*weather_location, time=t) as local_weather:
                    writer.writerow({k: v
                                     for k, v
                                     in local_weather.currently._data.items()})


def read_weather_data(filepath='../precrime_data/weather_hist.csv',
                      local_timezone='America/New_York'):
    """Load in the file of stored historical weather data."""
    weather_hist = pd.read_csv(filepath)
    weather_hist['Local_Datetime'] = pd.to_datetime(
        weather_hist['time'], unit='s'
    ).dt.tz_localize('UTC').dt.tz_convert(local_timezone)
    weather_hist.set_index('Local_Datetime', inplace=True)
    return weather_hist


def add_hourgroups(weather_hist):
    """Add datetime columns to the data."""
    weather_hist['WEATHER_YEAR'] = weather_hist.index.year
    weather_hist['WEATHER_MONTH'] = weather_hist.index.month
    weather_hist['WEATHER_DAY'] = weather_hist.index.day
    weather_hist['WEATHER_HOUR'] = weather_hist.index.hour
    weather_hist['WEATHER_DAYOFWEEK'] = \
        weather_hist.index.dayofweek
    weather_hist['WEATHER_HOURGROUP'] = weather_hist['WEATHER_HOUR'].map(
        lambda x: 4 * (int(x) // 4)
    )


def load_weather_data(filepath='../precrime_data/weather_hist.csv',
                      local_timezone='America/New_York'):
    """Load in the file of stored weather data and add hourgroups."""
    weather_hist = read_weather_data(filepath, local_timezone)
    add_hourgroups(weather_hist)
    return weather_hist
