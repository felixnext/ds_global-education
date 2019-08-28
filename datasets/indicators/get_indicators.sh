#!/bin/bash

# Retrieval script for various economic indicators

wget -O child-mortality.zip http://api.worldbank.org/v2/en/indicator/SH.DYN.MORT?downloadformat=csv
wget -O income-lowest-20.zip http://api.worldbank.org/v2/en/indicator/SI.DST.FRST.20?downloadformat=csv
wget -O access-electricity.zip http://api.worldbank.org/v2/en/indicator/EG.ELC.ACCS.ZS?downloadformat=csv
wget -O pop-growth.zip http://api.worldbank.org/v2/en/indicator/SP.POP.GROW?downloadformat=csv

unzip '*.zip'
