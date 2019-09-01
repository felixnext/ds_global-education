'''
Helper functions to handle economic indicators.

author: Felix Geilert
'''

import numpy as np
import pandas as pd
import seaborn as sns
import os
from matplotlib import pyplot as plt

# TODO:
def _get_csv(file):
  datapath = "./datasets/indicators"
  return pd.read_csv(os.path.join(datapath, file), skiprows=4)

def retrieve_gdp():
  '''Retrieves the GDP values of the countries.'''
  return _get_csv("API_NY.GDP.MKTP.CD_DS2_en_csv_v2_126271.csv")

def retrieve_gdp_pc():
  ''''Retrieves GDP per Capita'''
  return _get_csv("API_NY.GDP.PCAP.PP.CD_DS2_en_csv_v2_126302.csv")

def retrieve_electricity():
  '''Retrieve Data of percentage of population with acccess to electricity.'''
  return _get_csv("API_EG.ELC.ACCS.ZS_DS2_en_csv_v2_126505.csv")

def retrieve_education_spending():
  '''Retreive percentage of GDP spend on education.'''
  return _get_csv("API_SE.XPD.TOTL.GD.ZS_DS2_en_csv_v2_126172.csv")

def retrieve_income():
  '''Retrieve percentage of income going to poorest 20 percent.'''
  return _get_csv("API_SI.DST.FRST.20_DS2_en_csv_v2_42586.csv")
