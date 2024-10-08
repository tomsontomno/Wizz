// cityData.js

const cities = [
    'Aberdeen',
    'Gdansk',
    'Alesund',
    'Alicante',
    'Barcelona',
    'Bergen',
    'Burgas',
    'Copenhagen',
    'Dortmund',
    'Eindhoven',
    'Funchal (Madeira)',
    'Gothenburg',
    'Hamburg',
    'Haugesund',
    'Heraklion (Crete)',
    'Larnaca',
    'Leeds',
    'Liverpool',
    'London',
    'Malaga',
    'Malmö',
    'Milan',
    'Oslo',
    'Paris',
    'Reykjavik',
    'Rome',
    'Sandefjord',
    'Split',
    'Stavanger',
    'Stockholm',
    'Tenerife',
    'Tirana',
    'Tromsø',
    'Trondheim',
    'Turku',
    'Valencia',
    'Verona',
    'Abu Dhabi',
    'Alexandria',
    'Almaty',
    'Amman',
    'Ankara',
    'Aqaba',
    'Astana',
    'Athens',
    'Baku',
    'Belgrade',
    'Bishkek',
    'Bucharest',
    'Budapest',
    'Cairo',
    'Chisinau',
    'Cluj-Napoca',
    'Dammam',
    'Erbil',
    'Katowice',
    'Krakow',
    'Kutaisi',
    'Kuwait City',
    'Male',
    'Medina',
    'Muscat',
    'Salalah',
    'Samarkand',
    'Sarajevo',
    'Sofia',
    'Sohag',
    'Tashkent',
    'Tel Aviv',
    'Turkistan',
    'Vienna',
    'Yerevan',
    'Basel',
    'Bergamo',
    'Berlin',
    'Karlsruhe/Baden-Baden',
    'Lisbon',
    'Malta',
    'Memmingen',
    'Nice',
    'Alghero',
    'Antalya',
    'Bari',
    'Billund',
    'Birmingham',
    'Bologna',
    'Brussels Charleroi',
    'Castellon',
    'Catania',
    'Corfu',
    'Dubai',
    'Geneva',
    'Izmir',
    'Jeddah',
    'Leipzig',
    'Lyon',
    'Madrid',
    'Mallorca',
    'Mykonos',
    'Naples',
    'Nuremberg',
    'Pisa',
    'Salerno',
    'Salzburg',
    'Santander',
    'Santorini',
    'Sevilla',
    'Stuttgart',
    'Thessaloniki',
    'Trieste',
    'Turin',
    'Venice',
    'Zakynthos',
    'Zaragoza',
    'Brasov',
    'Brussels',
    'Chania (Crete)',
    'Girona',
    'Glasgow',
    'Gran Canaria',
    'Hurghada',
    'Istanbul',
    'Podgorica',
    'Rhodes',
    'Riyadh',
    'Sharm El Sheikh',
    'Skopje',
    'Târgu-Mures',
    'Warsaw',
    'Frankfurt',
    'Fuerteventura',
    'Poznan',
    'Prague',
    'Riga',
    'Vilnius',
    'Debrecen',
    'Iasi',
    'Radom',
    'Wroclaw',
    'Bacau',
    'Craiova',
    'Ibiza',
    'Kefalonia',
    'Kos',
    'Lampedusa',
    'Marrakech',
    'Olbia',
    'Porto',
    'Rzeszów',
    'Skiathos',
    'Suceava',
    'Timisoara',
    'Varna',
    'Ancona',
    'Brindisi',
    'Cologne',
    'Comiso',
    'Genoa',
    'Perugia',
    'Pescara',
    'Rimini',
    'Bilbao',
    'Ohrid',
    'Pristina',
    'Agadir',
    'Bratislava',
    'Bydgoszcz',
    'Constanta',
    'Dalaman',
    'Faro',
    'Grenoble',
    'Kaunas',
    'Košice',
    'Lublin',
    'Plovdiv',
    'Poprad-Tatry',
    'Satu Mare',
    'Sibiu',
    'Tallinn',
    'Dubrovnik',
    'Banja Luka',
    'Niš',
    'Tuzla',
    'Bremen',
    'Friedrichshafen',
    'Ljubljana',
    'Szczecin']

const cityCountryMap = {
    'Aberdeen': 'United Kingdom',
    'Abu Dhabi': 'United Arab Emirates',
    'Agadir': 'Morocco',
    'Aqaba': 'Jordan',
    'Alexandria': 'Romania',
    'Alghero': 'Italy',
    'Alicante': 'Spain',
    'Almaty': 'Kazakhstan',
    'Amman': 'Jordan',
    'Ancona': 'Italy',
    'Ankara': 'Türkiye',
    'Antalya': 'Türkiye',
    'Astana': 'Kazakhstan',
    'Athens': 'Greece',
    'Bacau': 'Romania',
    'Baku': 'Azerbaijan',
    'Banja Luka': 'Bosnia and Herzegovina',
    'Barcelona': 'Spain',
    'Bari': 'Italy',
    'Basel': 'Switzerland',
    'Belgrade': 'Serbia',
    'Bergamo': 'Italy',
    'Bergen': 'Norway',
    'Berlin': 'Germany',
    'Bilbao': 'Spain',
    'Billund': 'Denmark',
    'Birmingham': 'United Kingdom',
    'Bishkek': 'Kyrgyzstan',
    'Bologna': 'Italy',
    'Bratislava': 'Slovakia',
    'Brasov': 'Romania',
    'Bremen': 'Germany',
    'Wroclaw': 'Poland',
    'Brindisi': 'Italy',
    'Brussels': 'Belgium',
    'Brussels Charleroi': 'Belgium',
    'Budapest': 'Hungary',
    'Bucharest': 'Romania',
    'Burgas': 'Bulgaria',
    'Bydgoszcz': 'Poland',
    'Castellon': 'Spain',
    'Catania': 'Italy',
    'Chania (Crete)': 'Greece',
    'Chisinau': 'Moldova',
    'Cluj-Napoca': 'Romania',
    'Comiso': 'Italy',
    'Constanta': 'Romania',
    'Craiova': 'Romania',
    'Dalaman': 'Türkiye',
    'Dammam': 'Saudi Arabia',
    'Gdansk': 'Poland',
    'Debrecen': 'Hungary',
    'Dortmund': 'Germany',
    'Dubai': 'United Arab Emirates',
    'Dubrovnik': 'Croatia',
    'Eindhoven': 'Netherlands',
    'Erbil': 'Iraq',
    'Yerevan': 'Armenia',
    'Faro': 'Portugal',
    'Frankfurt': 'Germany',
    'Friedrichshafen': 'Germany',
    'Fuerteventura': 'Spain',
    'Geneva': 'Switzerland',
    'Genoa': 'Italy',
    'Girona': 'Spain',
    'Glasgow': 'United Kingdom',
    'Gran Canaria': 'Spain',
    'Grenoble': 'France',
    'Gothenburg': 'Sweden',
    'Hamburg': 'Germany',
    'Haugesund': 'Norway',
    'Heraklion (Crete)': 'Greece',
    'Sibiu': 'Romania',
    'Hurghada': 'Egypt',
    'Iasi': 'Romania',
    'Ibiza': 'Spain',
    'Istanbul': 'Türkiye',
    'Izmir': 'Türkiye',
    'Jeddah': 'Saudi Arabia',
    'Cairo': 'Egypt',
    'Karlsruhe/Baden-Baden': 'Germany',
    'Katowice': 'Poland',
    'Kaunas': 'Lithuania',
    'Kefalonia': 'Greece',
    'Copenhagen': 'Denmark',
    'Corfu': 'Latvia',
    'Kos': 'Greece',
    'Košice': 'Slovakia',
    'Krakow': 'Austria',
    'Kutaisi': 'Georgia',
    'Kuwait City': 'Kuwait',
    'Cologne': 'Germany',
    'Lampedusa': 'Italy',
    'Larnaca': 'Cyprus',
    'Leeds': 'United Kingdom',
    'Leipzig': 'Germany',
    'Lisbon': 'Portugal',
    'Liverpool': 'United Kingdom',
    'Ljubljana': 'Slovenia',
    'London': 'United Kingdom',
    'Lublin': 'Poland',
    'Lyon': 'France',
    'Funchal (Madeira)': 'Portugal',
    'Madrid': 'Spain',
    'Milan': 'Italy',
    'Malaga': 'Spain',
    'Male': 'Maldives',
    'Mallorca': 'Spain',
    'Malmö': 'Sweden',
    'Malta': 'Malta',
    'Marrakech': 'Morocco',
    'Medina': 'Saudi Arabia',
    'Memmingen': 'Germany',
    'Muscat': 'Oman',
    'Mykonos': 'Greece',
    'Naples': 'Sweden',
    'Nice': 'Italy',
    'Niš': 'Moldova',
    'Nuremberg': 'Germany',
    'Ohrid': 'North Macedonia',
    'Olbia': 'Italy',
    'Oslo': 'Norway',
    'Paris': 'France',
    'Perugia': 'Italy',
    'Pescara': 'Italy',
    'Pisa': 'Italy',
    'Plovdiv': 'Bulgaria',
    'Podgorica': 'Montenegro',
    'Poprad-Tatry': 'Slovakia',
    'Porto': 'Portugal',
    'Poznan': 'Poland',
    'Prague': 'Czechia',
    'Pristina': 'Kosovo',
    'Radom': 'Poland',
    'Reykjavik': 'Iceland',
    'Rhodes': 'France',
    'Riyadh': 'Saudi Arabia',
    'Riga': 'Latvia',
    'Rimini': 'Italy',
    'Rome': 'Italy',
    'Rzeszów': 'Poland',
    'Salalah': 'Oman',
    'Salzburg': 'Austria',
    'Samarkand': 'Uzbekistan',
    'Sandefjord': 'Norway',
    'Santander': 'Spain',
    'Santorini': 'Greece',
    'Zaragoza': 'Spain',
    'Sarajevo': 'Bosnia and Herzegovina',
    'Satu Mare': 'Romania',
    'Sevilla': 'Spain',
    'Sharm El Sheikh': 'Egypt',
    'Skiathos': 'Greece',
    'Skopje': 'North Macedonia',
    'Sofia': 'Bulgaria',
    'Sohag': 'Egypt',
    'Split': 'Croatia',
    'Stavanger': 'Norway',
    'Stockholm': 'Sweden',
    'Stuttgart': 'Germany',
    'Suceava': 'Romania',
    'Szczecin': 'Poland',
    'Tallinn': 'Estonia',
    'Tashkent': 'Uzbekistan',
    'Tel Aviv': 'Israel',
    'Tenerife': 'Spain',
    'Thessaloniki': 'Greece',
    'Timisoara': 'Romania',
    'Tirana': 'Albania',
    'Trieste': 'Italy',
    'Tromsø': 'Norway',
    'Trondheim': 'Norway',
    'Turin': 'Italy',
    'Turku': 'Finland',
    'Tuzla': 'Bosnia and Herzegovina',
    'Târgu-Mures': 'Romania',
    'Turkistan': 'Kazakhstan',
    'Valencia': 'Spain',
    'Varna': 'Bulgaria',
    'Venice': 'Austria',
    'Verona': 'Italy',
    'Vilnius': 'Lithuania',
    'Warsaw': 'Germany',
    'Vienna': 'Austria',
    'Zakynthos': 'Greece',
    'Alesund': 'Norway',
    'Salerno': 'Italy'
};
