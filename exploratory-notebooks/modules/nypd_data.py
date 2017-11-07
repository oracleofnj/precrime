"""Functions for processing the core dataset."""
import numpy as np
import pandas as pd
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


def save_dated_felonies(output_file=None):
    """Read the original file, filter it, and save the result."""
    print('Starting ({0})...'.format(
        strftime("%Y-%m-%d %H:%M:%S", localtime())
    ))
    raw_data = read_orig_file()
    print('Saving filtered output ({0})...'.format(
        strftime("%Y-%m-%d %H:%M:%S", localtime())
    ))
    filter_raw_data(raw_data, output_file)
    print('Done ({0})'.format(strftime("%Y-%m-%d %H:%M:%S", localtime())))


def load_dated_felonies(data_path=None, filtered_file=None):
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
    return nypd_data[nypd_data['COMPLAINT_DATETIME'] >= '2006-01-02 00:00:00']


def save_clean_felonies(output_file=None):
    """Read the filtered file, do more filtering, and save the result."""
    if output_file is None:
        output_file = '../precrime_data/clean_felonies.csv'
    print('Starting ({0})...'.format(
        strftime("%Y-%m-%d %H:%M:%S", localtime())
    ))
    filtered_felonies = load_dated_felonies()
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
