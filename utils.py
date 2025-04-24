import requests 
import pandas as pd 
import json 
import matplotlib.pyplot as plt

def collectWeatherData():
    # Get MeteoStat URL 
    url = "https://meteostat.p.rapidapi.com"
    headers = {"x-rapidapi-key": "85864ca846mshd96c3c76ac7a9bdp1c9f0ajsn898c7e632234"}
    response = requests.get(url=url, headers=headers)

    # Get user-inputted city name and format 
    cityName = "Spokane"

    # MapBox setup
    access_token = "pk.eyJ1IjoiZGh1YmJzMiIsImEiOiJjbThhbjg5Z3owOGJoMmxwdnA3c3UyZHczIn0.1TPEU3YXobMFr_N_ptnngw"
    mapBoxURL = "https://api.mapbox.com/search/geocode/v6/forward?q="
    # Search for user-input city in url
    mapBoxURL += "{" + cityName + "}" + "&access_token=" + access_token
    mapBoxResponse = requests.get(mapBoxURL)

    # Get latitude and longitude of user's city 
    json_obj = mapBoxResponse.json()


    results = json_obj["features"][0]
    results = results["properties"]

    city_longitude = results["coordinates"]["longitude"]
    city_latitude = results["coordinates"]["latitude"]

    # Get weather id from MeteoStat
    id_url = url + "/stations/nearby?lat=" + str(city_latitude) + "&lon=" + str(city_longitude)
    id_response = requests.get(id_url, headers=headers)
    id_response = id_response.json()
    id_response = id_response["data"][0]
    weather_id = id_response["id"]

    # Get daily weather with id (with previous year 2/24/24-2/23/25 and in imperial units)
    daily_url = url + "/stations/daily?station=" + str(weather_id) + "&start=2024-02-24&end=2025-02-23&units=imperial"
    daily_response = requests.get(daily_url, headers=headers)
    daily_response = daily_response.json()
    daily_response = daily_response["data"]

    ###### IS THIS THE RIGHT WAY TO GATHER COLUMNS/SET INDEX? #############
    columns = ["date", "tavg", "tmin", "tmax", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun"]
    df = pd.DataFrame(daily_response)
    df.set_index("date", inplace=True)
    columns.remove("date")

    # Write to csv 
    df.to_csv(cityName + "_daily_weather.csv")

    # Clean missing values 
    for column in columns:
        if (df[column].isnull().sum() / 366) >= 0.5:
            df.pop(column)

    # Write cleaned DataFrame to a csv 
    df.to_csv(cityName + "_daily_weather_cleaned.csv")