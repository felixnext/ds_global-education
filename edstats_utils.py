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
    This list can be used to filter aggregate scores from the data list.
    
    Args:
        df (pd.DataFrame): df_country DataFrame
    
    Returns:
        Updated dataframe with all aggregates filtered
    '''
    df_aggs = df[df['Special Notes'].fillna('').str.contains('aggregate')]
    return df_aggs['Country Code'].drop_duplicates().tolist()

def normalize_population(df, df_data, interpolate=False, popk=True):
    '''Normalizes the data from the relevant 
    
    Args:
        df (pd.DataFrame): Dataframe in `df_data` format containing the relevant information (should contain 'Country Code' column for matching)
        df_data (pd.DataFrame): Original `df_data` Dataframe
        interpolate (bool): Defines if missing data in population should be interpolated
        popk (bool): Defines if the population should be normalized (unit is `people`, normalize it to `thousand people` to be aligned with certain indicators)
        
    Returns:
        DataFrame in same format as `df` but with normalized values according to population in countries
    '''
    # indicator for the total population in `df_data`
    pop_ind = "SP.POP.TOTL"
    
    # select the relevant data
    df_pop = df_data[df_data['Indicator Code'] == pop_ind]
    # eliminate total NaN data
    df_pop = df_pop[df_pop.iloc[:, 4:-1].isnull().min(axis=1) == False]
    
    # interpolate missing items (to avoid NaN in multiplications)
    df_pop_data = df_pop.iloc[:, 4:50]
    if interpolate:
        df_pop_data.interpolate(axis=1, inplace=True, limit_direction='both')
    # limit population data to relevant
    df_pop_data['Country Code'] = df_pop['Country Code']
    df_pop = df_pop_data
    
    # normalize the datasets
    df_new = df.reset_index().set_index(df['Country Code'])
    df_pop_norm = df_pop.set_index(df_pop['Country Code']).iloc[:, :-1]
    if popk: df_pop_norm = df_pop_norm / 1000
    df_new = df_new.combine(df_pop_norm, lambda s1, s2: s1/s2, overwrite=False)
    
    # reset the index to old value
    df_new = df.set_index(df['index']).drop('index')
    
    return df_new

def append_region(df, df_country):
    '''Uses the country dataframe to append the region to the given dataframe.
    
    Args:
        df (pd.DataFrame): DataFrame that should contain a `Country Code` column
        df_country (pd.DataFrame): The `df_country` dataframe from the dataset
       
    Returns:
        Dataframe in same format as `df` but with additional `Region` column
    '''
    return pd.merge(df, df_country[['Country Code', 'Region']], on='Country Code')

def _retrieve_indicator(df, reg_str):
    '''Retrieve all datapoints that contain the given indicator regex string.'''
    # retireve list of relevant indicator codes
    ls_inds = df[df['Indicator Name'].str.contains(reg_str, regex=True, case=False)]['Indicator Code'].tolist()
    # extract all relevant items
    return df[df['Indicator Code'].isin(ls_inds)]

def retrieve_wittgenstein_mean_schooling(df):
    '''Retrieve the Wittgenstein Projections for mean years of education across different age groups.
    
    TODO: Explain Wittgenstein
    
    Function should extract all relevant wittgenstein indicators
    
    Args:
        df (pd.DataFrame): df_data Dataframe
        
    Returns:
        Dataframe with all datapoints of the indicators and additional columns: `['indicator', 'age_group', 'gender']`
    '''
    # retireve indicator list
    df_witt = _retrieve_indicator(df, 'Wittgenstein Projection: Mean years of schooling')
    
    # break the description into relevant cols
    df_witt_groups = df_witt['Indicator Name'].str.extract('Wittgenstein Projection: (?P<indicator>.*?(?P<age_group>Age [0-9]+(-[0-9]+|\+)). (?P<gender>[\s\S]+))', expand=True)
    # merge relevant data together
    df_witt = pd.concat([df_witt, df_witt_groups[['indicator', 'age_group', 'gender']]], axis=1)
    
    return df_witt

def retrieve_wittgenstein_population(df):
    '''Retrieve the Wittgenstein Projections for Education of the Population.
    
    Args:
        df (pd.DataFrame): df_data DataFrame
        
    Returns:
        DataFrame with all datapoints of the indicators and additional columns: `['indicator', 'age_group', 'education', 'gender']`
    '''
    # retrieve the relevant information
    df_witt = _retrieve_indicator(df, 'Wittgenstein Projection: Population .* education')
    
    # break the description into relevant cols
    df_witt_groups = df_witt['Indicator Name'].str.extract('Wittgenstein Projection: (?P<indicator>.*?(?P<age_group>age [0-9]+(-[0-9]+|\+))? in thousands .*?\. (?P<education>[\s\S]+)\. (?P<gender>[\s\S]+))', expand=True)
    # merge relevant data together
    df_witt = pd.concat([df_witt, df_witt_groups[['indicator', 'age_group', 'education', 'gender']].fillna({'age_group': 'Total'})], axis=1)
    
    return df_witt

def retrieve_barrolee_population():
    '''Retrieve the Barro-Lee Indicators for education of different parts of the population in percentage.
    
    TODO: explain Barro-Lee
    
    Function should extract all relevant barro lee indicators
    
    Args:
        df (pd.DataFrame): df_data DataFrame
    '''
    # extract relevant data
    df_barro = _retrieve_indicator(df, 'Barro-Lee: Percentage of .*')
    
    # split data
    df_barro_groups = df_barro['Indicator Name'].str.extract('Barro-Lee: (?P<indicator>Percentage of[ ]?(?P<gender>female)? population[ ]?(?P<age_group>age [0-9]+(-[0-9]+|\+))? with (?P<schooling>[\s\S]+?)(\. (?P<completed>[\s\S]+))?$)', expand=True)
    # combine data
    df_barro = pd.concat([df_barro, df_barro_groups[['indicator', 'schooling', 'completed', 'age_group', 'gender']].fillna({'gender': 'total'})], axis=1)
    
    return df_barro
    
def retrieve_barrolee_years(df):
    '''Retrieve the Barro-Lee indicators for average years in different types of education.
    
    Args:
        df (pd.DataFrame): df_data DataFrame
    
    Returns:
        Dataframe with all datapoints for the indicator and additional columns: `['indicator', 'schooling', 'age_group', 'gender']`
    '''
    # retrieve data
    df_barro = _retrieve_indicator(df, 'Barro-Lee: Average years .*')
    
    # split data
    df_barro_groups = df_barro['Indicator Name'].str.extract('Barro-Lee: (?P<indicator>Average years of (?P<schooling>[\s\S]+), (?P<age_group>age [0-9]+(-[0-9]+|\+))?, (?P<gender>[\s\S]+))', expand=True)
    # combine data
    df_barro = pd.concat([df_barro, df_barro_groups[['indicator', 'schooling', 'age_group', 'gender']]], axis=1)
    
    return df_barro