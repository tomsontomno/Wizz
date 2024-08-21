city_name_map = {
    "Medina": "Madinah",
    "Breslau": "Wrocław",
    "Danzig": "Gdańsk",
    "Akaba": "Aqaba",
    "Muscat": "Muscat(Oman)",
    "Posen": "Poznań",
    "Genua": "Genoa(Italy)",
    "Mailand": "Milan",
    "Kairo": "Cairo",
    "Sohag": "Sohag(Egypt)"
}


def formated_city_name(name: str):
    try:
        return city_name_map[name]
    except KeyError:
        return name


"""
country_name_map = {
    "Magyarorszag": "Hungary",
    "Osterreich": "Austria",
    "Polska": "Poland",
    "Italia": "Italy",
    "Espana": "Spain",
    "Deutschland": "Germany",
    "Schweiz/Suisse/Svizzera/Svizra": "Switzerland",
    "Nederland": "Netherlands",
    "Sverige": "Sweden",
    "Danmark": "Denmark",
    "Suomi": "Finland",
    "France": "France",
    "Cesko": "Czech Republic",
    "Hrvatska": "Croatia",
    "Eesti": "Estonia",
    "Belgie / Belgique / Belgien": "Belgium",
    "Turkiye": "Turkey",
    "Shqiperia": "Albania",
    "Norge": "Norway",
    "Lietuva": "Lithuania",
    "Latvija": "Latvia",
    "Azrbaycan": "Azerbaijan",
    "Kosova / Kosovo": "Kosovo",
    "Crna Gora /  ": "Montenegro",
    "Maroc": "Morocco",
    "Malaysia": "Malaysia",
    "Island": "Iceland"
}


def formated_country_name(name: str):
    try:
        return country_name_map[name]
    except KeyError:
        return name
"""
