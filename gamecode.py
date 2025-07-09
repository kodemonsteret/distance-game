import geopy.distance
from geopy.geocoders import Nominatim
import os
import numpy as np
import pandas as pd
import time

cities = pd.read_csv("cities.csv", on_bad_lines="skip", delimiter=";")
geolocator = Nominatim(user_agent="my_geopy_app")

def citygame():
    coords = (55.68004068027785, 12.574885137312116)  # Reference point
    stop = False
    states = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
    diffs = []
    pdiffs = []
    while not stop:
        # Choose a random city
        n = np.random.randint(0, len(cities))
        # n = 17098 # Fixed index for testing purposes
        city_name = cities.iloc[n, 1]
        country = cities.iloc[n, 7]
        coord_str = cities.iloc[n, -1]

        try:
            location = geolocator.reverse(coord_str, timeout=10)
            address = location[0]
        except Exception as e:
            print("Geolocation failed, skipping city.")
            continue 

        # Normalize address and check for US state
        normalized_address = address.replace("_", " ").replace(",", "").lower()
        usstate = next((state for state in states if state.lower() in normalized_address), None)

        if usstate:
            city_name = f"{city_name}, {usstate}"

        if pd.isna(country):
            country = address.split()[-1]

        print(f"\nGuess the distance to: {city_name}, {country}")
        time.sleep(0.3)

        guess_input = input("Enter distance in km (or type 'break' to stop): ")
        if guess_input.lower() == "break":
            stop = True
            #delete the last printed code if break is given as input
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        try:
            guess = int(guess_input)
            dist = int(geopy.distance.distance(coords, coord_str).km)
            diff = abs(guess - dist)
            pdiff = (diff / dist) * 100 if dist != 0 else 0
            pdiff2 = round(pdiff, 2)
            print(f"The correct distance is {dist} km.")
            print(f"Your guess was off by {diff} km or {pdiff2}%.\n")
        except ValueError:
            print("Invalid input. Please enter a number or 'break'.\n")
        except Exception as e:
            print("Distance calculation failed.\n")
        diffs.append(diff)
        pdiffs.append(pdiff)
        currentp = sum(pdiffs) / len(pdiffs) if pdiffs else 0
        currentp = round(currentp, 2)
        print(f"Your average percentage difference is {currentp:.2f}%.\n")

    print("Game over. Thanks for playing!")
    print(f"Your average percentage difference was {currentp:.2f}% over {len(diffs)} guesses.")
    print(f"Your average absolute difference was {round(np.mean(diffs), 2)} km over {len(diffs)} guesses.")
    print(f"Your best guess was {min(diffs)} km off, and your worst guess was {max(diffs)} km off.")

