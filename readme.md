# Analysis of Global Education Statistics

This defines an analysis of global education statistics as provided by the world-bank. This code is related to my [medium article](https://medium.com/@felixnext92) about the topic.

## Getting Started

### Download the Data

The **EdStats** dataset has to be downloaded from kaggle directly. This can be done manually through the [website](https://www.kaggle.com/theworldbank/education-statistics/version/45#) (just unpack the `*.csv` files in the `datasets/edstats` folder). Alternatively, you can use the [`kaggle-cli`](https://github.com/Kaggle/kaggle-api) tools:

```bash
$ sudo pip install kaggle
# Go to your kaggle account page and click "Create API Token" and store the resulting kaggle.json file it under /home/USERNAME/.kaggle
$ kaggle datasets download theworldbank/education-statistics -f edstats-csv-zip-32-mb-.zip -p datasets/edstats --unzip
# in case the file was not unpacked:
$ cd datasets/edstats
$ unzip edstats-csv-zip-32-mb-.zip
```

To retrieve the **economic indicators**, simply execute the `get_indicators.sh` script:

```bash
$ cd datasets/indicators
$ ./get_indicators.sh
```

### Run the code

The entire code can be found in the jupyter notebooks. Just run `jupyter lab .`

(Assuming that you have [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/) installed).

Make sure, you have all requirements installed (see [setup notes](setup_notes.md) for instructions how to setup a jupyter kernel)

## Methodology

The analysis is grouped into different stages and jupyter notebooks, which can be found by their naming conventions:

* `1X_exp-<DATASET>.ipynb` - General exploration of the dataset to understand the schema and general trends (also general data cleaning to make meaningful statements)
* `2X_aly-<TOPIC>.ipynb` - Analysis of a specific question (might combine multiple datasets)
* `9X_pred-<TREND>.ipynb` - Training of a predictor to forecast or interpolate data for a specific trend

The general questions I wanted to answer where:

* How are the years of schooling related to the proficiency in skills such as math or reading?
* Which economic factors (e.g. GDP) have the largest influence (i.e. correlation) on general education?
* How do economic factors influence the education of male vs female students?
* Which skills develop at which amount of schooling stated over the influence of the relevant economic indicators?

## Data Sources

The analysis is based on the following datasets:

* **WorldBank Education Statistics** (version used here is from [kaggle](https://www.kaggle.com/theworldbank/education-statistics/version/45#) - There might be a newer version available on the [WorldBank Homepage](https://datatopics.worldbank.org/education/home))
* **Economic Indicators** from the WorldBank Data (can be found [here](https://data.worldbank.org/indicator) - the datasets folder contains a script to crawl the relevant data)

### Notable Findings

* The total population of a country does not match up with the combined sum of people from the wittgenstein indicators. (Assumption: The indicators do not consider parts of the population before the official entrance age for education - I therefore treat the remaining percentages in the `No Education` group)
