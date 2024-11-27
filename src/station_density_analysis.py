import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

def fetch_data():
    print("Fetching air pollution monitoring station data...")
    stations_url = "https://api.energyandcleanair.org/stations?country=GB,US,TR,PH,IN,TH&format=geojson"
    countries_url = "https://r2.datahub.io/clvyjaryy0000la0cxieg4o8o/main/raw/data/countries.geojson"
    
    stations = requests.get(stations_url).json()
    print("Fetching country boundary data...")
    countries = requests.get(countries_url).json()
    
    return stations, countries

def calculate_densities():
    # Fetch data
    stations, countries = fetch_data()
    
    print("Converting data to GeoDataFrames...")
    # Convert to GeoDataFrames and set CRS
    stations_gdf = gpd.GeoDataFrame.from_features(stations['features'])
    countries_gdf = gpd.GeoDataFrame.from_features(countries['features'])
    
    # Set CRS to WGS 84
    stations_gdf.set_crs(epsg=4326, inplace=True)
    countries_gdf.set_crs(epsg=4326, inplace=True)
    
    print("Filtering countries and calculating areas...")
    # Dictionary to map between different country code standards
    # The stations API uses 2-letter codes (ISO 3166-1 alpha-2, e.g., 'US')
    # The boundaries API uses 3-letter codes (ISO 3166-1 alpha-3, e.g., 'USA')
    # This mapping allows us to match countries between the two datasets
    country_codes = {
        'US': 'USA',  # United States
        'GB': 'GBR',  # United Kingdom
        'TR': 'TUR',  # Turkey
        'TH': 'THA',  # Thailand
        'PH': 'PHL',  # Philippines
        'IN': 'IND'   # India
    }
    
    # Filter countries and project to equal-area projection
    selected_countries = countries_gdf[countries_gdf['ISO_A3'].isin(country_codes.values())].copy()
    selected_countries = selected_countries.to_crs('ESRI:54009')  # Mollweide projection for accurate area calculation
    
    # Calculate areas in square kilometers
    selected_countries.loc[:, 'area_sqkm'] = selected_countries.geometry.area / 10**6
    
    print("Counting PM10 stations...")
    # Filter stations that measure PM10
    pm10_station_list = []
    for _, station in stations_gdf.iterrows():
        pollutants = station['pollutants']
        # Check if station measures PM10
        if isinstance(pollutants, list) and 'pm10' in pollutants:
            pm10_station_list.append(station)
    
    # Convert filtered stations back to GeoDataFrame
    pm10_stations = gpd.GeoDataFrame(pm10_station_list)
    # Count how many stations each country has
    station_counts = pm10_stations.groupby('country_id').size()
    
    print("Calculating station densities...")
    # Create results dataframe
    results = []
    for country_code_2, country_code_3 in country_codes.items():
        # Get country area using 3-letter code
        country_area = selected_countries[selected_countries['ISO_A3'] == country_code_3]['area_sqkm'].iloc[0]
        # Get station count using 2-letter code
        station_count = station_counts.get(country_code_2, 0)
        # Calculate density per 1000 square kilometers
        density = (station_count / country_area) * 1000
        
        results.append({
            'Country': selected_countries[selected_countries['ISO_A3'] == country_code_3]['ADMIN'].iloc[0],
            'PM10_Stations': station_count,
            'Area_sqkm': round(country_area, 2),
            'Density_per_1000sqkm': round(density, 4)
        })
    
    # Create and sort dataframe
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Density_per_1000sqkm', ascending=False)
    
    return results_df

def main():
    print("Starting PM10 station density analysis...")
    try:
        results = calculate_densities()
        print("\nPM10 Monitoring Station Density by Country:")
        print(results.to_string(index=False))
        
        # Save results to CSV
        results.to_csv('station_density_results.csv', index=False)
        print("\nResults have been saved to 'station_density_results.csv'")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()