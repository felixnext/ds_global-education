'''
Contains a list of functions relevant to analyze and clean data from the EdStats dataset.

author: Felix Geilert
'''

import numpy as np
import pandas as pd
import seaborn as sns
import os
from matplotlib import pyplot as plt

def list_indicators(str, df, debug=False):
    '''Lists the codes for all relevant indicators from the `df_data` dataframe, given a regex search string.
    
    Args:
        str (str): Regex infused search string
        df (pd.DataFrame): Dataframe to search in
        debug (bool): Prints the intermediary dataframe to cross-check the indicator names directly
    
    Returns:
        List of relevant indicator codes
    '''
    # select the relevant dataframe
    df = df[df['Indicator Name'].str.contains(str, regex=True)]
    
    # debug: check for output
    if debug:
        print(df[['Indicator Name', 'Indicator Code']].drop_duplicates())
    
    # convert to list
    return df['Indicator Code'].drop_duplicates().tolist()

def list_aggregates(df):
    '''Create a list of all aggregate country codes from the `df_country` dataframe.
    
    Args:
        df (pd.DataFrame): df_country DataFrame
    
    Returns:
        Updated dataframe with all aggregates filtered
    '''
    df_aggs = df[df['Special Notes'].fillna('').str.contains('aggregate')]
    return df_aggs['Country Code'].drop_duplicates().tolist()

def select_indicators(inds, df):
    '''Selects the relevant indicators from the dataframe.
    
    Args:
        inds (list): List of indicator codes
        df (pd.DataFrame): Pandas dataframe the data should be extracted from
    
    Returns:
        New Dataframe with only the relevant rows
    '''
    return df[df['Indicator Code'].isin(inds)]

def normalize_population(df, df_data):
    '''Normalizes the data from the relevant 
    
    '''
    # indicator for the total population in `df_data`
    pop_ind = "SP.POP.TOTL"