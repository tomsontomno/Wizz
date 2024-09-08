import json
import os


class Weights:
    def __init__(self, username: str = "default", template_name: str = "default"):
        self.username = username
        self.template_name = template_name
        self.city_weights = {}
        self.city_hard_switch = {}
        self.flight_weights = {}
        self.flight_hard_switch = {}
        self.route_weights = {}
        self.route_hard_switch = {}
        self.routes_weights = {}
        self.routes_hard_switch = {}
        self.static_city_restrictions = []
        self.dynamic_city_restrictions = []
        self.static_route_restrictions = []
        self.dynamic_route_restrictions = []

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_path = os.path.join(base_dir, 'data', self.username, self.template_name, 'settings.json')
        self.load_weights()

    def load_weights(self):
        with open(self.file_path, 'r') as file:
            settings = json.load(file)

            self.city_weights = settings.get("weights", {}).get("city", {})
            self.city_hard_switch = settings.get("weights", {}).get("city_hard_switch", {})

            self.flight_weights = settings.get("weights", {}).get("flight", {})
            self.flight_hard_switch = settings.get("weights", {}).get("flight_hard_switch", {})

            self.route_weights = settings.get("weights", {}).get("route", {})
            self.route_hard_switch = settings.get("weights", {}).get("route_hard_switch", {})

            self.routes_weights = settings.get("weights", {}).get("routes", {})
            self.routes_hard_switch = settings.get("weights", {}).get("routes_hard_switch", {})

            self.static_city_restrictions = settings.get("restrictions", {}).get("static", {}).get("city", [])
            self.dynamic_city_restrictions = settings.get("restrictions", {}).get("dynamic", {}).get("city", [])
            self.static_route_restrictions = settings.get("restrictions", {}).get("static", {}).get("route", [])
            self.dynamic_route_restrictions = settings.get("restrictions", {}).get("dynamic", {}).get("route", [])

    def save_restrictions(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                existing_restrictions = json.load(file)
        else:
            existing_restrictions = {
                "restrictions": {
                    "static": {"city": [], "route": []},
                    "dynamic": {"city": [], "route": []}
                }
            }

        # Merge the existing restrictions with the current restrictions, ensuring no duplicates
        existing_static_city = set(existing_restrictions["restrictions"]["static"]["city"])
        existing_static_route = set(tuple(route) for route in existing_restrictions["restrictions"]["static"]["route"])
        existing_dynamic_city = set(existing_restrictions["restrictions"]["dynamic"]["city"])
        existing_dynamic_route = set(
            tuple(route) for route in existing_restrictions["restrictions"]["dynamic"]["route"])

        updated_static_city = existing_static_city.union(self.static_city_restrictions)
        updated_static_route = existing_static_route.union(tuple(route) for route in self.static_route_restrictions)
        updated_dynamic_city = existing_dynamic_city.union(self.dynamic_city_restrictions)
        updated_dynamic_route = existing_dynamic_route.union(tuple(route) for route in self.dynamic_route_restrictions)

        # Convert sets back to lists
        existing_restrictions["restrictions"]["static"]["city"] = list(updated_static_city)
        existing_restrictions["restrictions"]["static"]["route"] = [list(route) for route in updated_static_route]
        existing_restrictions["restrictions"]["dynamic"]["city"] = list(updated_dynamic_city)
        existing_restrictions["restrictions"]["dynamic"]["route"] = [list(route) for route in updated_dynamic_route]

        # Save the updated restrictions back to the file
        with open(self.file_path, 'w') as file:
            json.dump(existing_restrictions, file, indent=4)

    def add_static_city_restriction(self, city_name: str):
        if city_name not in self.static_city_restrictions:
            self.static_city_restrictions.append(city_name)
            self.save_restrictions()
            print(f"Static city restriction added: {city_name}")
        else:
            print(f"Static city restriction already exists: {city_name}")

    def add_static_route_restriction(self, route: list):
        if route not in self.static_route_restrictions:
            self.static_route_restrictions.append(route)
            self.save_restrictions()
            print(f"Static route restriction added: {route}")
        else:
            print(f"Static route restriction already exists: {route}")

    def add_dynamic_city_restriction(self, city_name: str):
        if city_name not in self.dynamic_city_restrictions:
            self.dynamic_city_restrictions.append(city_name)
            self.save_restrictions()
            print(f"Dynamic city restriction added: {city_name}")
        else:
            print(f"Dynamic city restriction already exists: {city_name}")

    def add_dynamic_route_restriction(self, route: list):
        if route not in self.dynamic_route_restrictions:
            self.dynamic_route_restrictions.append(route)
            self.save_restrictions()
            print(f"Dynamic route restriction added: {route}")
        else:
            print(f"Dynamic route restriction already exists: {route}")

    def remove_static_city_restriction(self, city_name: str):
        if city_name in self.static_city_restrictions:
            self.static_city_restrictions.remove(city_name)
            self.save_restrictions()
            print(f"Static city restriction removed: {city_name}")
        else:
            print(f"Static city restriction not found: {city_name}")

    def remove_dynamic_city_restriction(self, city_name: str):
        if city_name in self.dynamic_city_restrictions:
            self.dynamic_city_restrictions.remove(city_name)
            self.save_restrictions()
            print(f"Dynamic city restriction removed: {city_name}")
        else:
            print(f"Dynamic city restriction not found: {city_name}")

    def remove_static_route_restriction(self, route: list):
        if route in self.static_route_restrictions:
            self.static_route_restrictions.remove(route)
            self.save_restrictions()
            print(f"Static route restriction removed: {route}")
        else:
            print(f"Static route restriction not found: {route}")

    def remove_dynamic_route_restriction(self, route: list):
        if route in self.dynamic_route_restrictions:
            self.dynamic_route_restrictions.remove(route)
            self.save_restrictions()
            print(f"Dynamic route restriction removed: {route}")
        else:
            print(f"Dynamic route restriction not found: {route}")

    def clear_static_city_restrictions(self):
        self.static_city_restrictions = []
        self.save_restrictions()
        print("All static city restrictions cleared.")

    def clear_static_route_restrictions(self):
        self.static_route_restrictions = []
        self.save_restrictions()
        print("All static route restrictions cleared.")

    def clear_dynamic_city_restrictions(self):
        self.dynamic_city_restrictions = []
        self.save_restrictions()
        print("All dynamic city restrictions cleared.")

    def clear_dynamic_route_restrictions(self):
        self.dynamic_route_restrictions = []
        self.save_restrictions()
        print("All dynamic route restrictions cleared.")

    def get_all_city_restrictions(self):
        """
        Returns a list of all unique city restrictions, combining both static and dynamic restrictions.
        """
        return list(set(self.static_city_restrictions).union(self.dynamic_city_restrictions))

    def get_all_route_restrictions(self):
        """
        Returns a list of all unique route restrictions, combining both static and dynamic restrictions.
        Routes are represented as tuples to ensure uniqueness, but are returned as lists.
        """
        return [list(route) for route in set(tuple(route) for route in self.static_route_restrictions).union(
            tuple(route) for route in self.dynamic_route_restrictions)]

    def print_weights(self):
        print("City Weights:")
        print(json.dumps(self.city_weights, indent=2))

        print("\nCity Hard Switches:")
        print(json.dumps(self.city_hard_switch, indent=2))

        print("\nFlight Weights:")
        print(json.dumps(self.flight_weights, indent=2))

        print("\nFlight Hard Switches:")
        print(json.dumps(self.flight_hard_switch, indent=2))

        print("\nRoute Weights:")
        print(json.dumps(self.route_weights, indent=2))

        print("\nRoute Hard Switches:")
        print(json.dumps(self.route_hard_switch, indent=2))

        print("\nRoutes Weights:")
        print(json.dumps(self.routes_weights, indent=2))

        print("\nRoutes Hard Switches:")
        print(json.dumps(self.routes_hard_switch, indent=2))

        print("\nStatic Restricted Cities:")
        print(self.static_city_restrictions, "\n")

        print("\nStatic Restricted Routes:")
        print(self.static_route_restrictions)

        print("\nDynamic Restricted Cities:")
        print(self.dynamic_city_restrictions, "\n")

        print("\nDynamic Restricted Routes:")
        print(self.dynamic_route_restrictions, "\n")


if __name__ == "__main__":
    weights = Weights("tomsontomno", "template_test")
    print(weights.get_all_route_restrictions())
