from src.destination import Destination
from src.weights import Weights
from src.essentials import custom_sigmoid


def calculate_general_accessibility(city: Destination) -> float:
    value = city.get_accessibility_general() * 0.06 + custom_sigmoid(city.get_proximity_airport(), -49.34, 14.12, 0, True) * 0.4
    return value


def rate_city(city_name: str, weights: Weights) -> float:
    city_obj = Destination(city_name, username=weights.username, template_name=weights.template_name)
    rating = 0
    total_weight_sum = 0

    def check_and_restrict(condition):
        if condition:
            weights.add_dynamic_city_restriction(city_name)
        return

    # Check Hard Switches
    if weights.city_hard_switch.get("eu_member") == 1:
        check_and_restrict(not city_obj.get_country_eu_member())
    elif weights.city_hard_switch.get("eu_member") == 0:
        check_and_restrict(city_obj.get_country_eu_member())

    if weights.city_hard_switch.get("no_visa") == 1:
        check_and_restrict(not city_obj.get_country_visa_needed())
    elif weights.city_hard_switch.get("no_visa") == 0:
        check_and_restrict(city_obj.get_country_visa_needed())

    if weights.city_hard_switch.get("only_unvisited_city") == 1:
        check_and_restrict(city_obj.get_city_visited())
    elif weights.city_hard_switch.get("only_unvisited_city") == 0:
        check_and_restrict(not city_obj.get_city_visited())

    if weights.city_hard_switch.get("only_unvisited_country") == 1:
        check_and_restrict(city_obj.get_country_visited())
    elif weights.city_hard_switch.get("only_unvisited_country") == 0:
        check_and_restrict(not city_obj.get_country_visited())

    if weights.city_hard_switch.get("only_revisit") == 1:
        check_and_restrict(not city_obj.get_city_would_visit_again())
    elif weights.city_hard_switch.get("only_revisit") == 0:
        check_and_restrict(city_obj.get_city_would_visit_again())

    # Unvisited/Visited City
    if weights.city_weights.get("unvisited_city") != 0 or weights.city_weights.get("visited_city") != 0:
        if weights.city_weights.get("unvisited_city") != 0:
            rating += weights.city_weights.get("unvisited_city") * (not city_obj.get_city_visited())
        else:
            rating += weights.city_weights.get("visited_city") * city_obj.get_city_visited()
        total_weight_sum += max(weights.city_weights.get("unvisited_city"),
                                weights.city_weights.get("visited_city"))

    # Unvisited/Visited Country
    if weights.city_weights.get("unvisited_country") != 0 or weights.city_weights.get("visited_country") != 0:
        if weights.city_weights.get("unvisited_country") != 0:
            rating += weights.city_weights.get("unvisited_country") * (not city_obj.get_country_visited())
        else:
            rating += weights.city_weights.get("visited_country") * city_obj.get_country_visited()
        total_weight_sum += max(weights.city_weights.get("unvisited_country"),
                                weights.city_weights.get("visited_country"))

    # High/Low Rated City
    city_pref = city_obj.get_city_preferability()
    if weights.city_weights.get("high_rated_city") != 0 or weights.city_weights.get("low_rated_city") != 0:
        if weights.city_weights.get("high_rated_city") != 0:
            rating += weights.city_weights.get("high_rated_city") * city_pref / 10
        else:
            rating += weights.city_weights.get("low_rated_city") * (10 - city_pref) / 10
        total_weight_sum += max(weights.city_weights.get("high_rated_city"),
                                weights.city_weights.get("low_rated_city"))

    # High/Low Rated Country
    country_pref = city_obj.get_country_preferability()
    if weights.city_weights.get("high_rated_country") != 0 or weights.city_weights.get("low_rated_country") != 0:
        if weights.city_weights.get("high_rated_country") != 0:
            rating += weights.city_weights.get("high_rated_country") * country_pref / 10
        else:
            rating += weights.city_weights.get("low_rated_country") * (10 - country_pref) / 10
        total_weight_sum += max(weights.city_weights.get("high_rated_country"),
                                weights.city_weights.get("low_rated_country"))

    # Revisits/No Revisits
    if weights.city_weights.get("revisits") != 0 or weights.city_weights.get("no_revisits") != 0:
        if weights.city_weights.get("revisits") != 0:
            rating += weights.city_weights.get("revisits") * city_obj.get_city_would_visit_again()
        else:
            rating += weights.city_weights.get("no_revisits") * (not city_obj.get_city_would_visit_again())
        total_weight_sum += max(weights.city_weights.get("revisits"), weights.city_weights.get("no_revisits"))

    # Accessibility General/Not Accessibility General
    if weights.city_weights.get("accessibility_general") != 0 or weights.city_weights.get(
            "not_accessibility_general") != 0:
        if weights.city_weights.get("accessibility_general") != 0:
            rating += weights.city_weights.get("accessibility_general") * calculate_general_accessibility(city_obj)
        else:
            rating += weights.city_weights.get("not_accessibility_general") * (1 - calculate_general_accessibility(city_obj))
        total_weight_sum += max(weights.city_weights.get("accessibility_general"),
                                weights.city_weights.get("not_accessibility_general"))

    # Proximity Airport
    if weights.city_weights.get("near_city_airport") != 0 or weights.city_weights.get(
            "far_city_airport") != 0:
        if weights.city_weights.get("near_city_airport") != 0:
            rating += weights.city_weights.get("near_city_airport") * custom_sigmoid(city_obj.get_proximity_airport(), -49.34, 14.12, 0, True)
        else:
            rating += weights.city_weights.get("far_city_airport") * (1 - custom_sigmoid(city_obj.get_proximity_airport(), -49.34, 14.12, 0, True))
        total_weight_sum += max(weights.city_weights.get("near_city_airport"),
                                weights.city_weights.get("far_city_airport"))

    # Accessibility by Foot/Not Accessibility by Foot
    if weights.city_weights.get("accessibility_foot") != 0 or weights.city_weights.get(
            "not_accessibility_foot") != 0:
        if weights.city_weights.get("accessibility_foot") != 0:
            rating += weights.city_weights.get("accessibility_foot") * city_obj.get_reachability_by_foot() / 10
        else:
            rating += weights.city_weights.get("not_accessibility_foot") * (
                        10 - city_obj.get_reachability_by_foot()) / 10
        total_weight_sum += max(weights.city_weights.get("accessibility_foot"),
                                weights.city_weights.get("not_accessibility_foot"))

    # Accessibility by Public Transport/Not Accessibility by Public Transport
    if weights.city_weights.get("accessibility_transport") != 0 or weights.city_weights.get(
            "not_accessibility_transport") != 0:
        if weights.city_weights.get("accessibility_transport") != 0:
            rating += weights.city_weights.get(
                "accessibility_transport") * city_obj.get_reachability_by_public_transport() / 10
        else:
            rating += weights.city_weights.get("not_accessibility_transport") * (
                    10 - city_obj.get_reachability_by_public_transport()) / 10
        total_weight_sum += max(weights.city_weights.get("accessibility_transport"),
                                weights.city_weights.get("not_accessibility_transport"))

    # Cheap Transport/Expensive Transport
    if weights.city_weights.get("cheap_transport") != 0 or weights.city_weights.get("expensive_transport") != 0:
        if weights.city_weights.get("cheap_transport") != 0:
            rating += weights.city_weights.get("cheap_transport") * city_obj.get_cost_of_reachability() / 10
        else:
            rating += weights.city_weights.get("expensive_transport") * (
                        10 - city_obj.get_cost_of_reachability()) / 10
        total_weight_sum += max(weights.city_weights.get("cheap_transport"),
                                weights.city_weights.get("expensive_transport"))

    # Visa Needed/No Visa Needed
    if weights.city_weights.get("visa_needed") != 0 or weights.city_weights.get("no_visa_needed") != 0:
        if weights.city_weights.get("visa_needed") != 0:
            rating += weights.city_weights.get("visa_needed") * city_obj.get_country_visa_needed()
        else:
            rating += weights.city_weights.get("no_visa_needed") * (not city_obj.get_country_visa_needed())
        total_weight_sum += max(weights.city_weights.get("visa_needed"), weights.city_weights.get("no_visa_needed"))

    # EU Member/Not EU Member
    if weights.city_weights.get("eu_member") != 0 or weights.city_weights.get("not_eu_member") != 0:
        if weights.city_weights.get("eu_member") != 0:
            rating += weights.city_weights.get("eu_member") * city_obj.get_country_eu_member()
        else:
            rating += weights.city_weights.get("not_eu_member") * (not city_obj.get_country_eu_member())
        total_weight_sum += max(weights.city_weights.get("eu_member"), weights.city_weights.get("not_eu_member"))

    # High Degree/Low Degree
    deg = city_obj.get_degree()
    if deg < 3:
        degree_rating = 0
    elif deg <= 15:
        degree_rating = custom_sigmoid(deg, 10.77, 2.58, 15.1, False)
    else:
        degree_rating = 1

    if weights.city_weights.get("high_degree") != 0 or weights.city_weights.get("low_degree") != 0:
        if weights.city_weights.get("high_degree") != 0:
            rating += weights.city_weights.get("high_degree") * degree_rating
        else:
            rating += weights.city_weights.get("low_degree") * (1 - degree_rating)
        total_weight_sum += max(weights.city_weights.get("high_degree"), weights.city_weights.get("low_degree"))

    # Normalize and return the final rating
    if total_weight_sum == 0:
        return 0
    else:
        rating = (rating / total_weight_sum) * 100
        return round(rating, 5)


if __name__ == '__main__':
    pass
    x = Weights("tomsontomno", "template_test")
    print(rate_city("Abu Dhabi", x))
