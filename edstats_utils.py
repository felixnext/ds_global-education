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
    
    Mean number of years spent in school by age group and gender. 
    Projections are based on collected census and survey data for the base year (around 2010) and the Medium Shared Socioeconomic Pathways (SSP2) projection model. 
    The SSP2 is a middle-of-the-road scenario that combines medium fertility with medium mortality, medium migration, and the Global Education Trend (GET) education scenario.
    
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
    
    Share of the population of the stated age group that has completed upper secondary or incomplete post-secondary education as the highest level of educational attainment. 
    Projections are based on collected census and survey data for the base year (around 2010) and the Medium Shared Socioeconomic Pathways (SSP2) projection model. 
    The SSP2 is a middle-of-the-road scenario that combines medium fertility with medium mortality, medium migration, and the Global Education Trend (GET) education scenario. 
    
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

def retrieve_barrolee_percentage(df):
    '''Retrieve the Barro-Lee Indicators for education of different parts of the population in percentage.
    
    Percentage of population of the stated group that has completed or incompleted education of the stated type.
    
    Args:
        df (pd.DataFrame): df_data DataFrame
        
    Returns:
        Dataframe with all datapoints for the indicator and additional columns: `['indicator', 'schooling', 'completed', 'age_group', 'gender']`
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
    
    Average years of stated schooling in the given age group.
    total is the average years of stated education completed among people in the given group.
    
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

def retrieve_education_length(df):
    '''Retrieves the theoretical length of different types of education.
    
    Theoretical duration of stated education in years.
    
    Args:
        df (pd.DataFrame): df_data DataFrame
    
    Returns:
        Dataframe with all datapoints for the indicator and additional columns: `['education']`
    '''
    # retrieve data
    df_edu = _retrieve_indicator(df, 'Theoretical duration of .* education \(years\)')
    
    # split data
    df_edu_groups = df_edu['Indicator Name'].str.extract('Theoretical duration of (?P<education>[\s\S]+) education (years)', expand=True)
    df_edu = pd.concat([df_edu, df_edu_groups[['education']]], axis=1)
    
    return df_edu

def retrieve_gdp_education_institution(df):
    '''Retrieve Indicators related to GDP expenditure in education institutions.
    
    Government expenditure in stated institution as % of GDP (%)  
    
    Args:
        df (pd.DataFrame): df_data DataFrame
    
    Returns:
        Dataframe with all datapoints for the indicator and additional columns: `[institution]`
    '''
    # retrieve data
    df_gdp = _retrieve_indicator(df, 'Government expenditure in .* as % of GDP \(%\)')
    
    # split data
    df_gdp_groups = df_gdp['Indicator Name'].str.extract('Government expenditure in (?P<institution>[\s\S]+) as % of GDP (%)', expand=True)
    df_gdp = pd.concat([df_gdp, df_gdp_groups[['institution']]], axis=1)
    
    return df_gdp

def retrieve_gdp_education(df):
    '''Retrieve Indicators related to GDP expenditure for education.
    
    Government expenditure in stated education form as % of GDP (%)  
    
    Args:
        df (pd.DataFrame): df_data DataFrame
    
    Returns:
        Dataframe with all datapoints for the indicator and additional columns: `[education]`
    '''
    # retrieve data
    df_gdp = _retrieve_indicator(df, 'Government expenditure on .* education as % of GDP \(%\)')
    
    # split data
    df_gdp_groups = df_gdp['Indicator Name'].str.extract('Government expenditure on (?P<education>[\s\S]+) education as % of GDP (%)', expand=True)
    df_gdp = pd.concat([df_gdp, df_gdp_groups[['education']]], axis=1)
    
    return df_gdp

def retrieve_skill_llece(df):
    '''Retrieve the proficiency on various skills on LLECE levels in % of entire population.
    
    Percentage of stated grade students in the given proficiency level on the LLECE scale for the subject. 
    Data reflects country performance in the stated year according to LLECE reports.
    
    Args:
        df (pd.DataFrame): df_data DataFrame
    
    Returns:
        DataFrame with all datapoints for the indicators and additional columns `[indicator, gender, grade, subject, level]`
    '''
    # retrieve relevant data
    df_skill = _retrieve_indicator(df, 'LLECE: .* students by .* proficiency level')
    
    # extract columns
    df_skill_groups = df_skill['Indicator Name'].str.extract('LLECE: (?P<indicator>(?P<gender>(Male|Female))?[ ]*(?P<grade>[0-9]+(rd|th) grade) students by (?P<subject>.*?) proficiency level \(%\)\. (?P<level>[\S ]+))', expand=True)
    df_skill = pd.concat([df_skill, df_skill_groups[['indicator', 'gender', 'grade', 'subject', 'level']].fillna({'gender': 'Total'})], axis=1)
    
    return df_skill

def retrieve_skill_pisa(df):
    '''Retrieve 
    
    Percentage of 15-year-old students at the given proficiency level on the PISA subject scale. 
    Data reflects country performance in the stated year according to PISA reports, but may not be comparable across years or countries.
    
    Args:
        df (pd.DataFrame): df_data Dataframe
    
    Returns:
        DataFrame with all datapoints for the indicators and additional columns `[indicator, gender, subject, level]`
    '''
    # retrieve relevant data
    df_skill = _retrieve_indicator(df, 'PISA: .* proficiency level')
    
    # extract columns
    df_skill_groups = df_skill['Indicator Name'].str.extract('PISA: (?P<indicator>(?P<gender>(Male|Female))?[ ]*[0-9]+-year-olds by (?P<subject>.*?) proficiency level \(%\)\. (?P<level>[\S ]+))', expand=True)
    df_skill = pd.concat([df_skill, df_skill_groups[['indicator', 'gender', 'subject', 'level']].fillna({'gender': 'Total'})], axis=1)
    
    return df_skill

def retrieve_skill_timss(df):
    '''Retrieve 
    
    Stated grade students reaching the given international benchmark of achievement in the given subject in (%). 
    They are the share of given grade students scoring in the given achievement bracket on the subject assessment. 
    Data reflects country performance in the stated year according to TIMSS reports, but may not be comparable across years or countries.
    
    Args:
        df (pd.DataFrame): df_data Dataframe
    
    Returns:
        DataFrame with all datapoints for the indicators and additional columns `[indicator, gender, subject, achievement]`
    '''
    # retrieve relevant data
    df_skill = _retrieve_indicator(df, 'TIMSS: .* achievement')
    
    # extract columns
    df_skill_groups = df_skill['Indicator Name'].str.extract('TIMSS: (?P<indicator>(?P<gender>(Male|Female))?[ ]*(?P<grade>.*) grade students (?P<achievement>(reaching the .*?|who did not reach the low) international benchmark) of (?P<subject>.*) achievement \(%\))', expand=True)
    df_skill = pd.concat([df_skill, df_skill_groups[['indicator', 'gender', 'subject', 'achievement']].fillna({'gender': 'Total'})], axis=1)
    
    return df_skill

def retrieve_skill_piaac(df):
    '''Retrieve the relevant PIAAC Data for
    
    The Programme for the International Assessment of Adult Competencies (PIAAC) is a programme of assessment and analysis of adult skills. 
    The major survey conducted as part of PIAAC is the Survey of Adult Skills. 
    The Survey measures adults proficiency in key information-processing skills - literacy, numeracy and problem solving - and gathers information and data on how adults use their skills at home, at work and in the wider community.
    
    PIAAC: Adults by literacy proficiency level (%). Below Level 1
    PIAAC: Adults by proficiency level in problem solving in technology-rich environments (%). Below Level 1
    PIAAC: Female adults by numeracy proficiency level (%). Below Level 1
    
    Args:
        df (pd.DataFrame): df_data Dataframe
    
    Returns:
        DataFrame with all datapoints for the indicators and additional columns `[indicator, gender, subject, achievement]`
    '''
    # retrieve relevant data
    df_skill = _retrieve_indicator(df, 'PIAAC: .* proficiency level')
    
    # extract columns
    df_skill_groups = df_skill['Indicator Name'].str.extract('PIAAC: (?P<indicator>(?P<gender>(Male|Female|Young))?[ ]*[aA]dults by .*?(?P<subject>((?<=proficiency level in ).*|.*(?= proficiency level))).*? \(%\). (?P<level>[\S ]+))', expand=True)
    df_skill = pd.concat([df_skill, df_skill_groups[['indicator', 'gender', 'subject', 'level']].fillna({'gender': 'Total'})], axis=1)
    
    return df_skill

def filter_years(df, years):
    '''Takes a dataframe and filters only the year columns (leaves all other columns intact).
    
    Args:
        df (pd.DataFrame): Dataframe to be filtered
        years (list): list of year strings to be filtered for
        
    Returns:
        Dataframe with all relevant columns but only the data columns for the given year
    '''
    # generate a list of data
    ls_years = list(range(1970, 2018)) + list(range(2020, 2101, 5))
    ls_years = [str(y) for y in ls_years if str(y) not in years]
    # drop the irrelevant years
    return df.drop(ls_years, axis=1)