"""Functions for processing the core dataset."""
import numpy as np
import pandas as pd
import datetime
import csv
from time import localtime, strftime
from collections import defaultdict


def read_orig_file(data_path=None, orig_file=None):
    """Read the original data file into a pandas DataFrame.

    Parameters
    ----------
    data_path : string, optional
        directory containing original file
    orig_file : string, optional
        filename containing original file

    Returns
    -------
    raw_data : DataFrame

    """
    orig_file_defaults = {
        'data_path': '../precrime_data/',
        'orig_file': 'NYPD_Complaint_Data_Historic.csv',
        'dtype': {
            'CMPLNT_NUM': np.int64,
            'CMPLNT_FR_DT': str,
            'CMPLNT_FR_TM': str,
            'RPT_DT': str,
            'KY_CD': np.int32,
            'OFNS_DESC': str,
            'LAW_CAT_CD': str,
            'BORO_NM': str,
            'ADDR_PCT_CD': str,
            'Latitude': np.float64,
            'Longitude': np.float64
        },
        'index_col': 'CMPLNT_NUM',
        'usecols': [
            'CMPLNT_NUM',
            'CMPLNT_FR_DT',
            'CMPLNT_FR_TM',
            'RPT_DT',
            'KY_CD',
            'OFNS_DESC',
            'LAW_CAT_CD',
            'BORO_NM',
            'ADDR_PCT_CD',
            'Latitude',
            'Longitude'
        ],
        'parse_dates_cols': ['RPT_DT'],
    }

    if data_path is None:
        data_path = orig_file_defaults['data_path']
    if orig_file is None:
        orig_file = orig_file_defaults['orig_file']

    raw_data = pd.read_csv(
        filepath_or_buffer=data_path + orig_file,
        index_col=orig_file_defaults['index_col'],
        usecols=orig_file_defaults['usecols'],
        dtype=orig_file_defaults['dtype'],
        parse_dates=orig_file_defaults['parse_dates_cols'],
        infer_datetime_format=True,
    )
    return raw_data


def filter_raw_data(raw_data, output_file=None):
    """Get rid of useless rows.

    Removes non-felonies or rows with nonexistent report dates.

    Parameters
    ----------
    raw_data : DataFrame
    output_file : string

    Returns
    -------
    nypd_data : DataFrame
    """
    if output_file is None:
        output_file = '../precrime_data/raw_dated_felonies.csv'

    raw_data.dropna(
        subset=['CMPLNT_FR_DT', 'CMPLNT_FR_TM']
    )
    raw_data = raw_data[raw_data['LAW_CAT_CD'] == 'FELONY']
    raw_data = raw_data[pd.to_numeric(
        raw_data['ADDR_PCT_CD'],
        errors='coerce'
    ).fillna(-1) != -1]
    raw_data.to_csv(output_file)


def save_dated_felonies(data_path=None, orig_file=None, output_file=None):
    """Read the original file, filter it, and save the result."""
    print('Starting ({0})...'.format(
        strftime("%Y-%m-%d %H:%M:%S", localtime())
    ))
    raw_data = read_orig_file(data_path, orig_file)
    print('Saving filtered output ({0})...'.format(
        strftime("%Y-%m-%d %H:%M:%S", localtime())
    ))
    filter_raw_data(raw_data, output_file)
    print('Done ({0})'.format(strftime("%Y-%m-%d %H:%M:%S", localtime())))


def load_dated_felonies(data_path=None, filtered_file=None, datetime='2006-01-02 00:00:00' ):
    """Load in the file that has been filtered for valid dates."""
    filtered_file_defaults = {
        'data_path': '../precrime_data/',
        'filtered_file': 'raw_dated_felonies.csv',
        'dtype': {
            'CMPLNT_NUM': np.int64,
            'CMPLNT_FR_DT': str,
            'CMPLNT_FR_TM': str,
            'RPT_DT': str,
            'KY_CD': np.int32,
            'OFNS_DESC': str,
            'BORO_NM': str,
            'ADDR_PCT_CD': np.int32,
            'Latitude': np.float64,
            'Longitude': np.float64,
        },
        'index_col': 'CMPLNT_NUM',
        'usecols': [
            'CMPLNT_NUM',
            'CMPLNT_FR_DT',
            'CMPLNT_FR_TM',
            'RPT_DT',
            'KY_CD',
            'OFNS_DESC',
            'BORO_NM',
            'ADDR_PCT_CD',
            'Latitude',
            'Longitude',
        ],
        'parse_dates_dict': {
            'COMPLAINT_DATETIME': ['CMPLNT_FR_DT', 'CMPLNT_FR_TM'],
            'REPORT_DATE': ['RPT_DT'],
        },
    }

    if data_path is None:
        data_path = filtered_file_defaults['data_path']
    if filtered_file is None:
        filtered_file = filtered_file_defaults['filtered_file']

    nypd_data = pd.read_csv(
        filepath_or_buffer=data_path + filtered_file,
        index_col=filtered_file_defaults['index_col'],
        usecols=filtered_file_defaults['usecols'],
        dtype=filtered_file_defaults['dtype'],
        parse_dates=filtered_file_defaults['parse_dates_dict'],
        infer_datetime_format=True,
    )
    nypd_data['COMPLAINT_DATETIME'] = pd.to_datetime(
        nypd_data['COMPLAINT_DATETIME'],
        errors='coerce'
    )
    nypd_data.dropna(subset=['COMPLAINT_DATETIME'])
    # Exclude weird data on 2006-01-01.
    return nypd_data[nypd_data['COMPLAINT_DATETIME'] >= datetime]


def save_clean_felonies(data_path=None, filtered_file=None, output_file=None):
    """Read the filtered file, do more filtering, and save the result."""
    if output_file is None:
        output_file = '../precrime_data/clean_felonies.csv'
    print('Starting ({0})...'.format(
        strftime("%Y-%m-%d %H:%M:%S", localtime())
    ))
    filtered_felonies = load_dated_felonies(data_path, filtered_file)
    print('Done ({0})'.format(strftime("%Y-%m-%d %H:%M:%S", localtime())))
    filtered_felonies.to_csv(output_file)


def load_clean_felonies(data_path=None, clean_file=None):
    """Load in the fully cleaned and filtered file."""
    clean_file_defaults = {
        'data_path': '../precrime_data/',
        'clean_file': 'clean_felonies.csv',
        'dtype': {
            'CMPLNT_NUM': np.int64,
            'COMPLAINT_DATETIME': str,
            'REPORT_DATE': str,
            'KY_CD': np.int32,
            'OFNS_DESC': str,
            'BORO_NM': str,
            'ADDR_PCT_CD': np.int32,
            'Latitude': np.float64,
            'Longitude': np.float64,
        },
        'index_col': 'CMPLNT_NUM',
        'usecols': [
            'CMPLNT_NUM',
            'COMPLAINT_DATETIME',
            'REPORT_DATE',
            'KY_CD',
            'OFNS_DESC',
            'BORO_NM',
            'ADDR_PCT_CD',
            'Latitude',
            'Longitude',
        ],
        'parse_dates_cols': ['REPORT_DATE', 'COMPLAINT_DATETIME'],
    }

    if data_path is None:
        data_path = clean_file_defaults['data_path']
    if clean_file is None:
        clean_file = clean_file_defaults['clean_file']

    nypd_data = pd.read_csv(
        filepath_or_buffer=data_path+clean_file,
        index_col=clean_file_defaults['index_col'],
        usecols=clean_file_defaults['usecols'],
        dtype=clean_file_defaults['dtype'],
        parse_dates=clean_file_defaults['parse_dates_cols'],
        infer_datetime_format=True,
    )

    nypd_data.sort_values(by='COMPLAINT_DATETIME', inplace=True)
    return nypd_data


def add_offense_category(df):
    """Add an 'OFFENSE' category to the dataframe.

    This uses our own mapping of NYPD codes to categories we'll be
    trying to predict.
    """
    offense_category = defaultdict(lambda: 'Other')

    offense_category[101] = 'Homicide'
    offense_category[102] = 'Homicide'
    offense_category[103] = 'Homicide'

    offense_category[104] = 'Rape'
    offense_category[116] = 'Rape'

    offense_category[105] = 'Robbery'           # Mugging
    offense_category[106] = 'FelonyAssault'
    offense_category[107] = 'Burglary'          # Breaking and entering
    offense_category[109] = 'GrandLarceny'
    offense_category[110] = 'GrandLarcenyAuto'

    offense_category[112] = 'Fraud'
    offense_category[113] = 'Forgery'
    offense_category[114] = 'Arson'
    offense_category[117] = 'Drugs'
    offense_category[118] = 'Weapons'
    offense_category[121] = 'CriminalMischief'  # Graffiti

    df['OFFENSE'] = df['KY_CD'].map(offense_category).astype('category')
    df['OFFENSE'].cat.set_categories([
        'Homicide', 'Rape', 'Robbery', 'FelonyAssault',
        'Burglary', 'GrandLarceny', 'GrandLarcenyAuto',
        'Fraud', 'Forgery', 'Arson', 'Drugs',
        'Weapons', 'CriminalMischief', 'Other'
    ], inplace=True)


def add_datetime_columns(nypd_data):
    """Add datetime columns to the data."""
    nypd_data['COMPLAINT_YEAR'] = nypd_data['COMPLAINT_DATETIME'].dt.year
    nypd_data['COMPLAINT_MONTH'] = nypd_data['COMPLAINT_DATETIME'].dt.month
    nypd_data['COMPLAINT_DAY'] = nypd_data['COMPLAINT_DATETIME'].dt.day
    nypd_data['COMPLAINT_HOUR'] = nypd_data['COMPLAINT_DATETIME'].dt.hour
    nypd_data['COMPLAINT_DAYOFWEEK'] = \
        nypd_data['COMPLAINT_DATETIME'].dt.dayofweek
    nypd_data['COMPLAINT_HOURGROUP'] = nypd_data['COMPLAINT_HOUR'].map(
        lambda x: 4 * (int(x) // 4)
    )
    nypd_data['COMPLAINT_ID'] = nypd_data.index.values


def pivot_felonies(nypd_data):
    """Pivot the data and aggregate it in a useful way."""
    # First we pivot the data to sum up offenses by category.
    pivoted = nypd_data.pivot_table(
        index=[
            nypd_data['COMPLAINT_YEAR'],
            nypd_data['COMPLAINT_MONTH'],
            nypd_data['COMPLAINT_DAY'],
            nypd_data['COMPLAINT_HOURGROUP'],
            'ADDR_PCT_CD',   # These are not duplicated across boros.
        ],
        values='KY_CD',
        columns='OFFENSE',
        fill_value=0,
        aggfunc=len
    )
    # Unfortunately, the resulting pivot table has rows for dates that don't
    # actually exist since it uses the cross product of years and months,
    # resulting in rows for nonexistent dates like February 30th.
    #
    # To fix this, we create an empty dataframe with the correct values in the
    # index, and then merge the two dataframes.
    first_time = nypd_data['COMPLAINT_DATETIME'].min()
    first_date = datetime.date(
        first_time.year,
        first_time.month,
        first_time.day
    )
    last_time = nypd_data['COMPLAINT_DATETIME'].max()
    last_date = datetime.date(
        last_time.year,
        last_time.month,
        last_time.day
    )
    one_day = datetime.timedelta(days=1)
    dates_in_dataset = []
    d = first_date
    while d <= last_date:
        dates_in_dataset.append(d)
        d += one_day
    hourgroups = nypd_data['COMPLAINT_HOURGROUP'].unique()
    precinct_codes = nypd_data['ADDR_PCT_CD'].unique()
    # The cross-product of days, hourgroups, and precincts is what we want.
    # We make an empty dataframe with the correct index,
    # get the year/month/day back out, and then reset the index.
    empty_df = pd.DataFrame(index=pd.MultiIndex.from_product(
        [sorted(dates_in_dataset), sorted(hourgroups), sorted(precinct_codes)],
        names=[u'date', u'COMPLAINT_HOURGROUP', u'ADDR_PCT_CD']
    ))
    empty_df['COMPLAINT_YEAR'] = empty_df.index.get_level_values(0).year
    empty_df['COMPLAINT_MONTH'] = empty_df.index.get_level_values(0).month
    empty_df['COMPLAINT_DAY'] = empty_df.index.get_level_values(0).day
    empty_df['COMPLAINT_HOURGROUP'] = empty_df.index.get_level_values(1)
    empty_df['ADDR_PCT_CD'] = empty_df.index.get_level_values(2)
    empty_df['COMPLAINT_DAYOFWEEK'] = \
        empty_df.index.get_level_values(0).dayofweek
    empty_df.set_index([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY',
            'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD'
        ],
        inplace=True
    )
    correct_pivots = empty_df.merge(
        pivoted,
        how='left', left_index=True, right_index=True
    )
    # Finally, add in the complaint IDs so we can cross reference vs
    # the original table if desired.
    correct_pivots['COMPLAINT_IDS'] = nypd_data.groupby([
        'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD']
    )['COMPLAINT_ID'].agg(lambda x: ' '.join([str(i) for i in x]))
    correct_pivots['COMPLAINT_IDS'] = \
        correct_pivots['COMPLAINT_IDS'].fillna(value='')
    return correct_pivots


def save_pivoted_felonies(nypd_data, data_path=None, pivot_file=None):
    """Pivot the data and write the pivot table out to disk."""
    pivot_file_defaults = {
        'data_path': '../precrime_data/',
        'pivot_file': 'pivoted_felonies.csv',
    }
    if data_path is None:
        data_path = pivot_file_defaults['data_path']
    if pivot_file is None:
        pivot_file = pivot_file_defaults['pivot_file']
    pivoted = pivot_felonies(nypd_data)
    pivoted.to_csv(data_path + pivot_file, quoting=csv.QUOTE_NONNUMERIC)


def load_pivoted_felonies(data_path=None, pivot_file=None):
    """Load the saved, pivoted data."""
    pivot_file_defaults = {
        'data_path': '../precrime_data/',
        'pivot_file': 'pivoted_felonies.csv',
    }
    if data_path is None:
        data_path = pivot_file_defaults['data_path']
    if pivot_file is None:
        pivot_file = pivot_file_defaults['pivot_file']
    pivoted = pd.read_csv(
        data_path + pivot_file,
        index_col=[0, 1, 2, 3, 4],
        dtype={'ADDR_PCT_CD': int,
     'Arson': int,
     'Burglary': int,
     'COMPLAINT_DAY': int,
     'COMPLAINT_DAYOFWEEK': int,
     'COMPLAINT_HOURGROUP': int,
     'COMPLAINT_IDS': str,
     'COMPLAINT_MONTH': int,
     'COMPLAINT_YEAR': int,
     'CriminalMischief': int,
     'Drugs': int,
     'FelonyAssault': int,
     'Forgery': int,
     'Fraud': int,
     'GrandLarceny': int,
     'GrandLarcenyAuto': int,
     'Homicide': int,
     'Other': int,
     'Rape': int,
     'Robbery': int,
     'Weapons': int}
    )
    pivoted['COMPLAINT_IDS'] = pivoted['COMPLAINT_IDS'].fillna(value='')
    return pivoted
