from src.destination import Destination
from src.weights import Weights
from src.essentials import custom_sigmoid


# returns rating, weight
def rate_degree_transition(departure_degree, arrival_degree, low_threshold, high_threshold, weights, threshold_not_met_relief_factor=6):
    if weights.flight_weights.get("degree_level_up") == 0 and weights.flight_weights.get("degree_level_down") == 0:
        return 0, 0

    degree_diff = arrival_degree - departure_degree
    if degree_diff == 0:
        return 0, max(weights.flight_weights.get("degree_level_up"), weights.flight_weights.get("degree_level_down"))

    if degree_diff > 0:
        ratio = max(arrival_degree, departure_degree) / min(arrival_degree, departure_degree)
        if weights.flight_weights.get("degree_level_up") == 0:
            if departure_degree <= low_threshold and \
                    arrival_degree >= high_threshold:
                return 0, weights.flight_weights.get("degree_level_down")
            else:
                return 0, weights.flight_weights.get("degree_level_down") / threshold_not_met_relief_factor
        else:
            if departure_degree <= low_threshold and \
                    arrival_degree >= high_threshold:
                return min(1.0, custom_sigmoid(degree_diff, 4.32, 0.67, 15, False)) * \
                       min(1.0, custom_sigmoid(ratio, 1.68, 0.497, 4, False)), \
                       weights.flight_weights.get("degree_level_up")
            else:
                return 0, weights.flight_weights.get("degree_level_up") / threshold_not_met_relief_factor
    else:
        degree_diff *= -1
        temp = departure_degree
        departure_degree = arrival_degree
        arrival_degree = temp
        del temp

        ratio = min(arrival_degree, departure_degree) / max(arrival_degree, departure_degree)
        if weights.flight_weights.get("degree_level_down") == 0:
            if departure_degree <= low_threshold and \
                    arrival_degree >= high_threshold:
                return 0, weights.flight_weights.get("degree_level_up")
            else:
                return 0, weights.flight_weights.get("degree_level_up") / threshold_not_met_relief_factor
        else:
            if departure_degree <= low_threshold and \
                    arrival_degree >= high_threshold:
                return min(1.0, custom_sigmoid(degree_diff, 4.32, 0.67, 15, False)) * \
                       min(1.0, custom_sigmoid(ratio, 1.68, 0.497, 4, False)), \
                       weights.flight_weights.get("degree_level_down")
            else:
                return 0, weights.flight_weights.get("degree_level_down") / threshold_not_met_relief_factor


def rate_flight(departure_city: str, arrival_city: str, weights: Weights) -> float:
    departure_city_obj = Destination(departure_city, username=weights.username, template_name=weights.template_name)
    arrival_city_obj = Destination(arrival_city, username=weights.username, template_name=weights.template_name)

    rating = 0
    total_weight_sum = 0

    def check_and_restrict(condition):
        if condition:
            weights.add_dynamic_route_restriction([departure_city, arrival_city])
        return

    # Check Hard Switches
    if weights.flight_hard_switch.get("only_eu261") == 1:
        check_and_restrict(not arrival_city_obj.get_country_eu_member())
    elif weights.flight_hard_switch.get("only_eu261") == 0:
        check_and_restrict(arrival_city_obj.get_country_eu_member())

    if weights.flight_hard_switch.get("only_level_up") == 1:
        check_and_restrict(departure_city_obj.get_degree() >= arrival_city_obj.get_degree())
    elif weights.flight_hard_switch.get("only_level_up") == 0:
        check_and_restrict(not (departure_city_obj.get_degree() >= arrival_city_obj.get_degree()))

    # High/Low Distance
    distance = departure_city_obj.get_distance_to(arrival_city_obj.city)
    if weights.flight_weights.get("high_distance") != 0 or weights.flight_weights.get("low_distance") != 0:
        if weights.flight_weights.get("high_distance") != 0:
            rating += weights.flight_weights.get("high_distance") * (
                    1 - custom_sigmoid(distance, 840, 700, 170, True))
        else:
            rating += weights.flight_weights.get("low_distance") * custom_sigmoid(distance, 840, 700, 170, True)
        total_weight_sum += max(weights.flight_weights.get("high_distance"), weights.flight_weights.get("low_distance"))

    # EU 261 / No EU 261
    if weights.flight_weights.get("eu_261") != 0 or weights.flight_weights.get("no_eu_261") != 0:
        if weights.flight_weights.get("eu_261") != 0:
            rating += weights.flight_weights.get("eu_261") * (
                    arrival_city_obj.get_country_eu_member() or departure_city_obj.get_country_eu_member())
        else:
            rating += weights.flight_weights.get("no_eu_261") * (
                not (arrival_city_obj.get_country_eu_member() or departure_city_obj.get_country_eu_member()))
        total_weight_sum += max(weights.flight_weights.get("eu_261"), weights.flight_weights.get("no_eu_261"))

    # High/Low Airport Rating
    airport_rating = arrival_city_obj.get_airport_rating()
    if weights.flight_weights.get("high_airport_rating") != 0 or weights.flight_weights.get("low_airport_rating") != 0:
        if weights.flight_weights.get("high_airport_rating") != 0:
            rating += weights.flight_weights.get("high_airport_rating") * airport_rating / 10
        else:
            rating += weights.flight_weights.get("low_airport_rating") * (10 - airport_rating) / 10
        total_weight_sum += max(weights.flight_weights.get("high_airport_rating"),
                                weights.flight_weights.get("low_airport_rating"))

    rated, weight = rate_degree_transition(departure_city_obj.get_degree(), arrival_city_obj.get_degree(), 4, 9, weights)
    rating += rated * weight
    total_weight_sum += weight

    # Normalize and return the final rating
    if total_weight_sum == 0:
        return 0
    else:
        rating = (rating / total_weight_sum) * 100
        return round(rating, 5)


if __name__ == '__main__':
    pass
    x = Weights("tomsontomno", "template_test")
    a = "Cologne"
    b = "Abu Dhabi"
    print(rate_flight(b, a, x))
