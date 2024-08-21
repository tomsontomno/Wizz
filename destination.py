import json


def _get_city_info(city):
    with open('city_preferability.json', 'r') as file:
        city_data = json.load(file)
        return {
            "name": city,
            "visited": city_data[city][0],
            "preferability": city_data[city][1],
            "would_visit_again": city_data[city][2],
            "reachability_by_foot": city_data[city][3],
            "reachability_by_public_transport": city_data[city][4][0],
            "cost_of_reachability": city_data[city][4][1],
            "country": city_data[city][5]
        }


def _get_country_info(country):
    with open('country_preferability.json', 'r') as file:
        country_data = json.load(file)
        return {
            "visited": country_data[country][0],
            "preferability": country_data[country][1],
            "eu_member": country_data[country][2],
            "visa_needed": country_data[country][3],
            "german_name": country_data[country][4]
        }


def _get_continent(country):
    with open('continent_map.json', 'r') as file:
        continent_data = json.load(file)
        for continent, countries in continent_data.items():
            if country in countries:
                return continent
    print("Continent not found")
    return "Unknown"


class Destination:
    def __init__(self, city):
        self.city = city
        self.city_info = _get_city_info(city)
        self.country_info = _get_country_info(self.city_info['country'])
        self.continent = _get_continent(self.city_info['country'])

    # Getter methods for City information
    def get_city(self):
        return self.city

    def get_city_visited(self):
        return self.city_info['visited']

    def get_city_preferability(self):
        return self.city_info['preferability']

    def get_city_would_visit_again(self):
        return self.city_info['would_visit_again']

    def get_reachability_by_foot(self):
        return self.city_info['reachability_by_foot']

    def get_reachability_by_public_transport(self):
        return self.city_info['reachability_by_public_transport']

    def get_cost_of_reachability(self):
        return self.city_info['cost_of_reachability']

    def get_city_country(self):
        return self.city_info['country']

    # Getter methods for Country information
    def get_country(self):
        return self.country_info['german_name']

    def get_country_visited(self):
        return self.country_info['visited']

    def get_country_preferability(self):
        return self.country_info['preferability']

    def get_country_eu_member(self):
        return self.country_info['eu_member']

    def get_country_visa_needed(self):
        return self.country_info['visa_needed']

    # Getter method for Continent
    def get_continent(self):
        return self.continent

    def get_full_info(self):
        return {
            "City": self.get_city(),
            "City Info": {
                "Visited": self.get_city_visited(),
                "Preferability": self.get_city_preferability(),
                "Would Visit Again": self.get_city_would_visit_again(),
                "Reachability by Foot": self.get_reachability_by_foot(),
                "Reachability by Public Transport": self.get_reachability_by_public_transport(),
                "Cost of Reachability": self.get_cost_of_reachability()
            },
            "Country Info": {
                "Country": self.get_country(),
                "Visited": self.get_country_visited(),
                "Preferability": self.get_country_preferability(),
                "EU Member": self.get_country_eu_member(),
                "Visa Needed": self.get_country_visa_needed()
            },
            "Continent": self.get_continent()
        }
