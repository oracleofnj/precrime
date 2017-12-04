"""Functions to make crime predictions."""
import numpy as np
import pandas as pd
import datetime
import csv
from .weather import load_weather_data
from .nypd_data import load_pivoted_felonies
from .nyc_shapefiles import load_census_info
from sklearn.linear_model import Ridge


def load_all_data():
    """Load all the data, merge it, and return a single dataframe."""
    weather_hist = load_weather_data()
    pivoted_felonies = load_pivoted_felonies()
    precinct_df, tract_df, intersection_df = load_census_info()

    merged_data = pivoted_felonies.reset_index().merge(
        weather_hist,
        how='left',
        left_on=['COMPLAINT_YEAR', 'COMPLAINT_MONTH',
                 'COMPLAINT_DAY', 'COMPLAINT_HOURGROUP'],
        right_on=['WEATHER_YEAR', 'WEATHER_MONTH',
                  'WEATHER_DAY', 'WEATHER_HOURGROUP'],
    ).merge(
        precinct_df,
        how='left',
        left_on='ADDR_PCT_CD',
        right_index=True
    )[[
        'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD', 'COMPLAINT_DAYOFWEEK',
        'apparentTemperature', 'cloudCover', 'dewPoint', 'humidity', 'icon',
        'nearestStormBearing', 'nearestStormDistance', 'ozone',
        'precipIntensity', 'precipProbability', 'precipType', 'pressure',
        'summary', 'temperature', 'time', 'uvIndex', 'visibility',
        'windBearing', 'windGust', 'windSpeed',
        'PrecinctShapefileID', 'Population', 'Median_Household_Income',
        'Percent_Bachelors_Degree',
        'Homicide', 'Rape', 'Robbery', 'FelonyAssault', 'Burglary',
        'GrandLarceny', 'GrandLarcenyAuto', 'Fraud', 'Forgery', 'Arson',
        'Drugs', 'Weapons', 'CriminalMischief', 'Other', 'COMPLAINT_IDS',
    ]]
    return merged_data


def split_into_X_y(merged_data):
    """Split the merged data into the X (features) and y (data) portions."""
    X = merged_data[[
        'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD', 'COMPLAINT_DAYOFWEEK',
        'apparentTemperature', 'cloudCover', 'dewPoint', 'humidity', 'icon',
        'nearestStormBearing', 'nearestStormDistance', 'ozone',
        'precipIntensity', 'precipProbability', 'precipType', 'pressure',
        'summary', 'temperature', 'time', 'uvIndex', 'visibility',
        'windBearing', 'windGust', 'windSpeed',
        'PrecinctShapefileID', 'Population', 'Median_Household_Income',
        'Percent_Bachelors_Degree'
    ]]
    y = merged_data[[
        'Homicide', 'Rape', 'Robbery', 'FelonyAssault', 'Burglary',
        'GrandLarceny', 'GrandLarcenyAuto', 'Fraud', 'Forgery', 'Arson',
        'Drugs', 'Weapons', 'CriminalMischief', 'Other', 'COMPLAINT_IDS',
    ]]
    return X, y


def split_by_datetime(merged_data, test_times):
    """Split the dataset into training and test sets.

    Parameters
    ----------
    merged_data : DataFrame
        A DataFrame with columns 'COMPLAINT_YEAR', 'COMPLAINT_MONTH',
        'COMPLAINT_DAY', and 'COMPLAINT_HOURGROUP'

    test_times : DataFrame
        A DataFrame with columns 'TEST_YEAR', 'TEST_MONTH',
        'TEST_DAY', and 'TEST_HOURGROUP'
    """
    data_datecols = merged_data[['COMPLAINT_YEAR', 'COMPLAINT_MONTH',
                                 'COMPLAINT_DAY', 'COMPLAINT_HOURGROUP']]
    data_datecols.columns = ['year', 'month', 'day', 'hour']
    data_datetimes = pd.to_datetime(data_datecols)

    test_datecols = test_times[['TEST_YEAR', 'TEST_MONTH',
                                'TEST_DAY', 'TEST_HOURGROUP']]
    test_datecols.columns = ['year', 'month', 'day', 'hour']
    test_datetimes = pd.to_datetime(test_datecols)

    test_mask = data_datetimes.isin(test_datetimes)

    train_data = merged_data[~test_mask]
    test_data = merged_data[test_mask]

    return train_data, test_data


def precrime_train_test_split(merged_data, test_times):
    """Split the dataset into X_train, X_test, y_train, y_test.

    Parameters
    ----------
    merged_data : DataFrame
        A DataFrame with columns 'COMPLAINT_YEAR', 'COMPLAINT_MONTH',
        'COMPLAINT_DAY', and 'COMPLAINT_HOURGROUP'

    test_times : DataFrame
        A DataFrame with columns 'TEST_YEAR', 'TEST_MONTH',
        'TEST_DAY', and 'TEST_HOURGROUP'
    """
    train_data, test_data = split_by_datetime(merged_data, test_times)
    X_train, y_train = split_into_X_y(train_data)
    X_test, y_test = split_into_X_y(test_data)
    return X_train, X_test, y_train, y_test


def create_test_period(first_date, last_date):
    """Create a DataFrame covering a specific period of time."""
    one_day = datetime.timedelta(days=1)
    dates_in_dataset = []
    d = first_date
    while d < last_date:
        dates_in_dataset.append(d)
        d += one_day
    hourgroups = range(0, 24, 4)
    test_times = pd.DataFrame(index=pd.MultiIndex.from_product(
        [sorted(dates_in_dataset), sorted(hourgroups)],
    ))
    test_times['TEST_YEAR'] = test_times.index.get_level_values(0).year
    test_times['TEST_MONTH'] = test_times.index.get_level_values(0).month
    test_times['TEST_DAY'] = test_times.index.get_level_values(0).day
    test_times['TEST_HOURGROUP'] = test_times.index.get_level_values(1)
    test_times.reset_index(inplace=True)
    test_times.index.rename('Index', inplace=True)
    return test_times[[
        'TEST_YEAR', 'TEST_MONTH', 'TEST_DAY', 'TEST_HOURGROUP'
    ]]


def create_test_quarter(year, quarter):
    """Create a test mask for use with split_by_datetime.

    Parameters
    ----------
    year : integer
    quarter : integer from 1 to 4

    Returns
    -------
    test_times : DataFrame
        A DataFrame with columns 'TEST_YEAR', 'TEST_MONTH',
        'TEST_DAY', and 'TEST_HOURGROUP'
    """
    first_date = datetime.date(year, 3 * (quarter-1) + 1, 1)
    if quarter == 4:
        last_date = datetime.date(year+1, 1, 1)
    else:
        last_date = datetime.date(year, 3 * quarter + 1, 1)
    return create_test_period(first_date, last_date)


def create_finegrained_split(frac=0.1, random_state=4800):
    """Return a random 10% of the data as a test mask."""
    first_date = datetime.date(2006, 1, 2)
    last_date = datetime.date(2017, 1, 1)
    test_times = create_test_period(first_date, last_date)
    return test_times.sample(frac=frac, random_state=random_state)


def create_coarsegrained_split(n=5, random_state=4800):
    """Return a random 5 quarters as a test mask."""
    quarters = np.array([
        [year, quarter]
        for year in range(2006, 2017)
        for quarter in range(1, 5)
    ])
    if random_state is not None:
        np.random.seed(random_state)
    test_quarters = np.random.choice(len(quarters), size=n, replace=False)
    test_times = create_test_quarter(
        quarters[test_quarters[0], 0], quarters[test_quarters[0], 1]
    )
    for i in range(1, n):
        test_times = test_times.append(
            create_test_quarter(
                quarters[test_quarters[i], 0], quarters[test_quarters[i], 1]
            ),
            ignore_index=True
        )
    return test_times


def create_2016_split():
    """Create the entire year of 2016 as a test mask."""
    first_date = datetime.date(2016, 1, 1)
    last_date = datetime.date(2017, 1, 1)
    return create_test_period(first_date, last_date)


def save_splits(filepath='../precrime_data/'):
    """Create the train/test splits and save them to disk."""
    splits = {
        'fine': create_finegrained_split().sort_index(),
        'coarse': create_coarsegrained_split().sort_index(),
        '2016': create_2016_split().sort_index(),
    }
    for k, v in splits.items():
        v.to_csv(
            filepath + 'split_{0}.csv'.format(k),
            quoting=csv.QUOTE_NONNUMERIC
        )


def load_splits(filepath='../precrime_data/'):
    """Load the saved train/test splits from disk."""
    splits = ['fine', 'coarse', '2016']
    return {
        split: pd.read_csv(
            filepath + 'split_{0}.csv'.format(split),
            index_col=0
        )
        for split in splits
    }


def create_all_splits(crime_data, splits):
    """Create X_train, X_test, y_train, y_test for each split in splits.

    Parameters
    ----------
    crime_data : DataFrame
        A DataFrame with columns 'COMPLAINT_YEAR', 'COMPLAINT_MONTH',
        'COMPLAINT_DAY', and 'COMPLAINT_HOURGROUP', in the format returned by
        load_all_data().

    splits : dict
        A dictionary of {split_name : DataFrame}, in the format returned by
        load_splits().
    """
    return {
        k: precrime_train_test_split(crime_data, v)
        for k, v in splits.items()
    }


def sample_model(X_train, y_train, X_test):
    """Example model to perform ridge regression on each felony type."""
    def add_categorical_features(X):
        X_features = X[[
            'ADDR_PCT_CD',
            'COMPLAINT_MONTH',
            'temperature',
            'precipIntensity'
        ]].copy()
        X_features['COMPLAINT_DAY_HOUR'] = \
            X['COMPLAINT_DAYOFWEEK'].astype(str) + '_' + \
            X['COMPLAINT_HOURGROUP'].astype(str)
        return pd.get_dummies(
            X_features,
            columns=['ADDR_PCT_CD', 'COMPLAINT_MONTH', 'COMPLAINT_DAY_HOUR']
        )

    X_train_features = add_categorical_features(X_train)
    X_test_features = add_categorical_features(X_test)
    y_pred = X_test[[
        'COMPLAINT_YEAR',
        'COMPLAINT_MONTH',
        'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP',
        'ADDR_PCT_CD'
    ]].copy()

    y_train_dvs = y_train.select_dtypes(exclude=['object'])
    ridge = Ridge()
    ridge.fit(X_train_features, y_train_dvs)
    y_pred_dvs = ridge.predict(X_test_features)

    for i, crime_type in enumerate(y_train_dvs.columns):
        y_pred[crime_type] = y_pred_dvs[:, i]

    return y_pred
