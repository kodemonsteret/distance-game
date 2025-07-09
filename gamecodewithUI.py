# citygame_ui.py

import tkinter as tk
from tkinter import messagebox
import geopy.distance
from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd

cities = pd.read_csv("cities.csv", on_bad_lines="skip", delimiter=";")
geolocator = Nominatim(user_agent="my_geopy_app")


##     CHANGE THESE COORDINATES TO THE LOCATION YOU WANT TO USE AS A REFERENCE POINT   ##
#########################################################################################
REF_COORDS = (55.68004068027785, 12.574885137312116)
#########################################################################################
# This is set to a location in Copenhagen, Denmark (a bar called Farfars)
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}
uk_abbrev_to_region = {
    "ENG": "England",
    "WLS": "Wales",
    "SCT": "Scotland",
    "NIR": "Northern Ireland",
}
abbrev_to_state = {abbr: state for state, abbr in us_state_to_abbrev.items()}

def get_state_from_abbrev(x):
    return abbrev_to_state.get(x.upper())  # use upper() to normalize input
def get_region_from_abbrev(x):
    return uk_abbrev_to_region.get(x.upper())  # use upper() to normalize input
class CityGameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("City Distance Game")

        # --- LEFT SIDE ---
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.city_label = tk.Label(left_frame, text="City: ???", font=("Helvetica", 14))
        self.city_label.pack(pady=10)

        self.avg_label = tk.Label(left_frame, text="Average % difference: 0.00%", font=("Helvetica", 12))
        self.avg_label.pack(pady=5)

        self.entry = tk.Entry(left_frame, font=("Helvetica", 12))
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.process_guess)

        self.submit_btn = tk.Button(left_frame, text="Submit Guess", command=self.process_guess)
        self.submit_btn.pack(pady=5)

        self.quit_btn = tk.Button(left_frame, text="Quit", command=self.quit_game)
        self.quit_btn.pack(pady=5)

        # --- RIGHT SIDE: SCROLLABLE LOG ---
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        log_label = tk.Label(right_frame, text="Guess History", font=("Consolas", 15, "bold"))
        log_label.pack()

        self.log_text = tk.Text(right_frame, height=20, width=90, wrap=tk.NONE, font=("Consolas", 15))
        self.log_text.tag_configure("bold", font=("Consolas", 15, "bold"))
        self.log_text.tag_configure("green", foreground="green")
        self.log_text.tag_configure("red", foreground="red")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        header = (
            f"{'City':<40}"
            f"{'Actual':<20}"
            f"{'Guess':<20}"
            f"{'Δ (km)':<15}"
            f"{'%diff':<17}"
            f"{'Avg':<10}\n"
            + "-" * 120 + "\n"
        )
        self.log_text.insert(tk.END, header, "bold")

        scrollbar = tk.Scrollbar(right_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # --- GAME STATE ---
        self.diffs = []
        self.pdiffs = []
        self.guess_count = 0
        self.current_city = None
        self.current_coords = None
        self.running = True

        self.get_next_city()

    def get_next_city(self):
        tried = 0
        while tried < 10:
            tried += 1
            n = np.random.randint(0, len(cities))
            # n = 75138 # Fixed index for testing purposes
            city_name = cities.iloc[n, 1]
            country = cities.iloc[n, 7]
            coord_str = cities.iloc[n, -1]
            region = cities.iloc[n, 9]  # UK/US region code if applicable

            if pd.isna(city_name) or pd.isna(coord_str):
                continue

            if pd.isna(country):
                country = "Unknown"

            # Only reverse geocode if in the US
            display_name = f"{city_name}, {country}"
            country_str = str(country).strip().lower()
            if country_str in ["united states", "us", "usa"]:
                state = get_state_from_abbrev(region)
                if state:
                    display_name = f"{city_name}, {state}"
                else: 
                    display_name = f"{city_name}, {country}"
            elif country_str in ["united kingdom", "uk", "gb"]:
                country1 = get_region_from_abbrev(region)
                if country1:
                    display_name = f"{city_name}, {country1}"
                else:
                    display_name = f"{city_name}, United Kingdom"          
            self.current_city = display_name
            self.current_coords = coord_str
            self.city_label.config(text=f"City: {self.current_city}")
        return

    def process_guess(self, event=None):
        guess_input = self.entry.get().strip()
        if guess_input.lower() == "break":
            self.quit_game()
            return

        try:
            guess = int(guess_input)
        except ValueError:
            self.log_text.insert(tk.END, "⚠️ Invalid input. Please enter a number.\n")
            self.log_text.see(tk.END)
            return

        try:
            dist = int(geopy.distance.distance(REF_COORDS, self.current_coords).km)
            diff = abs(guess - dist)
            pdiff = (diff / dist) * 100 if dist != 0 else 0

            self.diffs.append(diff)
            self.pdiffs.append(pdiff)
            self.guess_count += 1
            currentp = round(sum(self.pdiffs) / len(self.pdiffs), 2)
            percent_str = f"{round(pdiff, 2):.2f}%"

            # Choose color tag for %diff
            if pdiff < 5:
                pct_tag = "green"
            elif pdiff > 15:
                pct_tag = "red"
            else:
                pct_tag = None  # default

            # Construct aligned fields
            city_field = f"[{self.guess_count}] {self.current_city}".ljust(40)
            actual_field = f"Actual: {dist} km".ljust(20)
            guess_field = f"Guess: {guess} km".ljust(20)
            diff_field = f"Δ: {diff} km".ljust(15)
            pct_field = f"%diff: ".ljust(9)
            avg_field = f"Avg: {currentp:.2f}%"

            # Insert log with tags
            self.log_text.insert(tk.END, city_field, "bold")
            self.log_text.insert(tk.END, actual_field, "bold")
            self.log_text.insert(tk.END, guess_field, "bold")
            self.log_text.insert(tk.END, diff_field, "bold")
            self.log_text.insert(tk.END, pct_field, "bold")

            # Insert %diff with color
            if pct_tag:
                self.log_text.insert(tk.END, percent_str.ljust(8), pct_tag)
            else:
                self.log_text.insert(tk.END, percent_str.ljust(8))

            #insert average
            self.log_text.insert(tk.END, avg_field + "\n", "bold")
            self.log_text.see(tk.END)
            self.avg_label.config(text=f"Average % difference: {currentp:.2f}%")
            self.entry.delete(0, tk.END)
            self.get_next_city()

        except Exception as e:
            self.log_text.insert(tk.END, f"❌ Error computing distance: {str(e)}\n")
            self.log_text.see(tk.END)

    def quit_game(self):
        self.running = False
        if self.pdiffs:
            currentp = round(sum(self.pdiffs) / len(self.pdiffs), 2)
            messagebox.showinfo("Game Over",
                                f"Average % difference: {currentp:.2f}% over {len(self.diffs)} guesses.\n"
                                f"Average absolute difference: {round(np.mean(self.diffs), 2)} km.\n"
                                f"Best guess: {min(self.diffs)} km off or {round(min(self.pdiffs),2)}%.\n"
                                f"Worst guess: {max(self.diffs)} km off or {round(max(self.pdiffs),2)}%")
        self.root.destroy()

# This function allows importing and running from another file
def run_game():
    root = tk.Tk()
    root.geometry("1600x600")
    CityGameUI(root)
    root.mainloop()