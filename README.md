# Air Quality Monitoring Station Density Analysis

This project analyzes the density of PM10 monitoring stations across different countries using public air quality data.


## Features

- Calculates PM10 monitoring station density per 1,000 square kilometers
- Analyzes data for US, UK, Turkey, Thailand, Philippines, and India
- Presents results in a ranked table format


## Installation

1. Clone the repository
```bash
git clone <url>.
```
2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate # On MACOS use: source venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage
Run the analysis script:
```bash
python src/station_density_analysis.py
```

The script will output a table showing:

- Country Name
- Number of PM10 Stations
- Area (in square kilometers)
- Density of PM10 Stations per 1,000 sq. km

- It is then stored in a CSV file named 'station_density_analysis.csv'

Requirements
- Python 3.8+
- See requirements.txt for package dependencies