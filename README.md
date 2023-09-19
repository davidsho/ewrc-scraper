# ewrc-scraper

Application containing helper functions for scraping the ewrc-results website

## Data Sets

The data folder contains:
- events.csv -- list of rally events from 2000
- results.csv -- list of rally results from 2000
- /entry-lists/{YEAR}-{ROUND}-entries.csv -- entry list for each event of each year 
- /leg-results/{YEAR}-{ROUND}-results.csv -- leg results for each event of each year

## Installation

Run `./setup.sh` to setup virtual environment and install dependencies

You need to create a `.env` file in the root directory with the following variables:
- `USERNAME` -- https://www.ewrc-results.com username
- `PASSWORD` -- https://www.ewrc-results.com password

## Usage

Run `./run.sh` to run the application and build the data sets using helper functions

`./core/ranker.ipynb` contains an example notebook for ranking drivers and co-drivers based on their results
