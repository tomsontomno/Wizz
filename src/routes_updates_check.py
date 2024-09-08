import os
from collections import Counter

# Paths to the files
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
old_file = os.path.join(base_dir, 'data', 'raw_routes_old.txt')
new_file = os.path.join(base_dir, 'data', 'raw_routes_latest.txt')

# Read the content of both files
with open(old_file, 'r') as file:
    old_routes = file.read().splitlines()

with open(new_file, 'r') as file:
    new_routes = file.read().splitlines()

# Convert the lists to sets for comparison
old_routes_set = set(old_routes)
new_routes_set = set(new_routes)

# Find added and removed routes
added_routes = new_routes_set - old_routes_set
removed_routes = old_routes_set - new_routes_set


# Count the number of flights per city
def count_city_routes(routes):
    city_counter = Counter()
    for route in routes:
        city1, city2 = route.split(' - ')
        city_counter[city1] += 1
        city_counter[city2] += 1
    return city_counter


old_city_counts = count_city_routes(old_routes)
new_city_counts = count_city_routes(new_routes)

# Find changes in the number of routes for each city
city_changes = {}
all_cities = set(old_city_counts.keys()).union(new_city_counts.keys())

for city in all_cities:
    old_count = old_city_counts.get(city, 0)
    new_count = new_city_counts.get(city, 0)
    if old_count != new_count:
        city_changes[city] = {'old': old_count, 'new': new_count}

# Output the results
print("Added routes:")
for route in sorted(added_routes):
    print(route)

print("\nRemoved routes:")
for route in sorted(removed_routes):
    print(route)

print("\nChanges in number of flights for each city:")
for city, counts in city_changes.items():
    print(f"{city}: {counts['old']} -> {counts['new']}")
