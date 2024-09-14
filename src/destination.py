import json
import os
from src.coordinates import proximity_to_airport
from src.essentials import get_Graph
from multiprocessing import Lock

lock = Lock()
G = get_Graph()


class Destination:
    def __init__(self, city, username="default", template_name="default"):
        self.city = city
        self.username = username
        self.template_name = template_name
        self.settings = self._load_settings()
        self.city_info = self._get_city_info(self.city)
        self.country_info = self._get_country_info(self.city_info['country'])
        self.continent = self.country_info['continent']

    def _load_settings(self):
        with lock:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            settings_path = os.path.join(base_dir, 'data', self.username, self.template_name, 'settings.json')

            with open(settings_path, 'r') as file:
                return json.load(file)

    def _get_city_info(self, city):
        city_data = self.settings['city'].get(city)
        if not city_data:
            raise ValueError(f"City '{city}' not found")
        return {
            "name": city,
            "visited": city_data['visited'],
            "rating": city_data['rating'],
            "revisit": city_data['revisit'],
            "airport_rating": city_data['airport_rating'],
            "proximity_airport": proximity_to_airport(city),
            "accessibility_general": city_data['accessibility_general'],
            "accessibility_foot": city_data['accessibility_foot'],
            "accessibility_transport": city_data['accessibility_transport'],
            "cheap_transport": city_data['cheap_transport'],
            "degree": G.degree(city),
            "country": city_data['country']
        }

    def _get_country_info(self, country):
        country_data = self.settings['country'].get(country)
        if not country_data:
            raise ValueError(f"Country '{country}' not found")
        return {
            "visited": country_data['visited'],
            "rating": country_data['rating'],
            "eu_member": country_data['eu_member'],
            "visa_needed": country_data['visa_needed'],
            "german_name": country_data['german_name'],
            "continent": country_data['continent']
        }

    # Getter methods for City information
    def get_city(self):
        return self.city

    def get_city_visited(self):
        return self.city_info['visited']

    def get_city_preferability(self):
        return self.city_info['rating']

    def get_city_would_visit_again(self):
        return self.city_info['revisit']

    def get_airport_rating(self):
        return self.city_info['airport_rating']

    def get_proximity_airport(self):
        return proximity_to_airport(self.city)

    def get_accessibility_general(self):
        return self.city_info['accessibility_general']

    def get_reachability_by_foot(self):
        return self.city_info['accessibility_foot']

    def get_reachability_by_public_transport(self):
        return self.city_info['accessibility_transport']

    def get_cost_of_reachability(self):
        return self.city_info['cheap_transport']

    def get_degree(self):
        return G.degree(self.city)

    def get_country_name_local(self):
        return self.city_info['country']

    # Getter methods for Country information
    def get_country_name_german(self):
        return self.country_info['german_name']

    def get_country_visited(self):
        return self.country_info['visited']

    def get_country_preferability(self):
        return self.country_info['rating']

    def get_country_eu_member(self):
        return self.country_info['eu_member']

    def get_country_visa_needed(self):
        return self.country_info['visa_needed']

    # Getter method for Continent
    def get_continent(self):
        return self.continent

    def get_full_info(self):
        return {
            "city": {
                "name": self.get_city(),
                "visited": self.get_city_visited(),
                "rating": self.get_city_preferability(),
                "revisit": self.get_city_would_visit_again(),
                "airport_rating": self.get_airport_rating(),
                "accessibility_general": self.get_accessibility_general(),
                "accessibility_foot": self.get_reachability_by_foot(),
                "accessibility_transport": self.get_reachability_by_public_transport(),
                "cheap_transport": self.get_cost_of_reachability(),
            },
            "country": {
                "name": self.get_country_name_local(),
                "visited": self.get_country_visited(),
                "rating": self.get_country_preferability(),
                "eu_member": self.get_country_eu_member(),
                "visa_needed": self.get_country_visa_needed(),
                "german_name": self.get_country_name_german(),
            },
            "continent": self.get_continent()
        }

    def get_distance_to(self, city: str) -> float:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        distances_json = os.path.join(base_dir, 'data', 'distances.json')

        with open(distances_json, 'r') as file:
            distances_data = json.load(file)

        if self.city in distances_data:
            if city in distances_data[self.city]:
                return distances_data[self.city][city]
            else:
                raise ValueError(f"Distance from {self.city} to {city} not found.")
        else:
            raise ValueError(f"City {self.city} not found in distances data.")


def print_city(city_name: str, username=None, template_name=None):
    city = Destination(city_name, username, template_name)

    # Print all available functions for the city object
    print("\nCity Name: " + city.get_city() + "\n")

    print("Visited: " + str(city.get_city_visited()))
    print("Rating: " + str(city.get_city_preferability()))
    print("Would Like to Visit Again: " + str(city.get_city_would_visit_again()))
    print("Airport Rating: " + str(city.get_airport_rating()) + "\n")
    print("General Accessibility: " + str(city.get_accessibility_general()))
    print("Reachability by Foot: " + str(city.get_reachability_by_foot()))
    print("Reachability by Public Transport: " + str(city.get_reachability_by_public_transport()))
    print("Cost of Reachability: " + str(city.get_cost_of_reachability()) + "\n")

    print("Country Name (local): " + city.get_country_name_local())
    print("Country Name (german): " + city.get_country_name_german())
    print("Country Rating: " + str(city.get_country_preferability()))
    print("Country Visited: " + str(city.get_country_visited()))
    print("Visa Needed: " + str(city.get_country_visa_needed()))
    print("EU Member: " + str(city.get_country_eu_member()) + "\n")

    # Print continent information
    print("Continent: " + city.get_continent() + "\n")

    # Print full information
    print("Full Info: ")
    print(city.get_full_info())


if __name__ == '__main__':
    pass
    print_city("Abu Dhabi")
    print_city("Abu Dhabi", username="tomsontomno", template_name="template_test")
