city_name_map = {
    "Alexandria": "Alexandria (Egypt",
    "Athens": "Athens (Greece)",
    "Belgrade": "Belgrade (Serbia)",
    "Medina": "Medina (Saudi-Arabia)",
    "Muscat": "Muscat (Oman)",
    "Rome": "Rome (Italy)",
    "Sohag": "Sohag (Egypt)",
    "Turkistan": "Mausoleum of Khoja Ahmed Yasawi",
    "Warsaw": "Warsaw (Poland)",
    "Niš": "Niš (Serbia)",
    "Gothenburg": "Gothenburg (Sweden)",
    "Brussels": "Brussels (Belgium)",
    "Corfu": "Corfu (Greece)",
    "Naples": "Naples (Italy)",
    "Rhodes": "Rhodes Greece",
    "Geneva": "Geneva (Switzerland)",
    "Nuremberg": "Nürnberg (Germany)",
    "Venice": "Venice (Italy)",
    "Alesund": "Nørvasundet (Norway)",
    "Genoa": "Genoa (Italy)",
    "Ibiza": "Puig d'en Valls (Balearic Islands)",
    "Kos": "Kos (Greece)",
    "Cologne": "Köln (Germany)"
}


def formatted_city_name(name: str):
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
