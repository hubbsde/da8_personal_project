from datetime import datetime
import requests 
import pandas as pd 
import json 
import matplotlib.pyplot as plt

def collectWeatherData():

    ##############################################
    #   This code is pulled from my DA4 repo.    #
    ##############################################

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

    
    columns = ["date", "tavg", "tmin", "tmax", "prcp", "snow", "wdir", "wspd", "wpgt", "pres", "tsun"]
    df = pd.DataFrame(daily_response)

    # Write to csv 
    df.to_csv(cityName + "_daily_weather.csv")

    # Clean missing values 
    for column in columns:
        if (df[column].isnull().sum() / 366) >= 0.5:
            df.pop(column)

    # Set date column to datetime objects 
    df["date"] = pd.to_datetime(df["date"])

    # Shorten to start time of recorded activities from devyn_strava_activities
    startDate = datetime.strptime("2024-5-13", "%Y-%m-%d")
    df = df[df["date"] >= startDate]

    df.set_index("date", inplace=True)

    # Write cleaned DataFrame to a csv 
    df.to_csv(cityName + "_CLEANED_daily_weather.csv")


def collectStravaData():

    # This collects AND cleans the data from devyn_strava_activities.csv

    df = pd.read_csv("devyn_strava_activities.csv")

    df_columns = df.columns
    df_cleaned = df.copy()
    exception_count = 0

    # Deleting columns without enough information
    for column in df_columns:

        try:
            
            # Delete any columns with more than 25% of 0 values
            if (df_cleaned[column]==0).sum() > (len(df_cleaned) * 0.25):
                df_cleaned = df_cleaned.drop(column, axis=1)

            # Delete any columns with more than 25% of null values
            if(df_cleaned[column].isnull()).sum() > (len(df_cleaned) * 0.25):
                df_cleaned = df_cleaned.drop(column, axis=1)

        # Catches any instances in which neither of the above instances prove true
        except Exception as e:
            
            exception_count+=1


    df_columns = df_cleaned.columns

    # Manually remove unnecessary columns
    df_cleaned = df_cleaned.drop("Filename", axis=1)
    df_cleaned = df_cleaned.drop("From Upload", axis=1)

    # I realized after the fact that pandas already does this, but I felt bad deleting my work
    """
    monthDecoder = {"Jan": 1, "Feb" : 2, "Mar" : 3, "Apr" : 4, "May" : 5, "Jun" : 6, "Jul" : 7, "Aug" : 8, "Sep" : 9, "Oct" : 10, "Nov" : 11, "Dec" : 12}
    for date in df_cleaned["Activity Date"]:
        month = date[:3]
        month = monthDecoder.get(month)
        month = str(month)
        
        day = date[4:6]
        day = day.strip(",")
        
        year = date[7:12]
        year = year.strip(",")
        year = year.strip(" ")

        modified_date = year + "-" + month + "-" + day
        date_obj = datetime.strptime(modified_date, "%Y-%m-%d")
        df_cleaned["Activity Date"] = df_cleaned["Activity Date"].replace(date, date_obj)
    """

    # Convert ["Activity Date"] to datetime objects 
    endingDate = datetime.strptime("2025-2-23", "%Y-%m-%d")
    df_cleaned["Activity Date"] = pd.to_datetime(df_cleaned["Activity Date"])
    df_cleaned = df_cleaned[df_cleaned["Activity Date"] <= endingDate]

    df_cleaned.set_index("Activity Date", inplace=True)

    # Write cleaned data to csv 
    df_cleaned.to_csv("devyn_CLEANED_strava_activities.csv")