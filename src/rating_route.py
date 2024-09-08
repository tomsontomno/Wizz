from src.weights import Weights
from src.essentials import custom_sigmoid, calculate_distance_cities, evaluate_weighting
from src.precompute import retrieve_precomputed_data
from numpy import mean, std


def rating_route(route: list, weights: Weights, original_start: str = "", original_end: str = "",
                 radius_start: float = 0, radius_end: float = 0):
    """
    Calculates the rating of an entire route based on various criteria.

    Args:
        route (list): A list of cities representing the route.
        original_start (str): The originally intended starting city.
        original_end (str): The originally intended arrival city.
        radius_start (float): Radius around the start city to search for airports.
        radius_end (float): Radius around the destination city to search for airports.
        weights (Weights): The weights object containing user preferences.
    Returns:
        float: The calculated rating of the route.
    """
    if len(route) < 2:
        return 0
    if original_start == "":
        original_start = route[0]
    if original_end == "":
        original_end = route[-1]
    if not weights:
        weights = Weights()
    if not weights:
        weights = Weights()
    precomputed_data = retrieve_precomputed_data(weights.username, weights.template_name)

    city_ratings_data = precomputed_data.get('city', {})
    route_ratings_data = precomputed_data.get('routes', {})

    rating = 0
    total_weight_sum = 0

    # Calculate Route Distance Rating
    direct_distance = calculate_distance_cities(original_start, original_end)
    total_distance = sum([calculate_distance_cities(route[i], route[i + 1]) for i in range(len(route) - 1)])

    distance_ratio = direct_distance / total_distance
    distance_ratio = custom_sigmoid(distance_ratio * 100, 76.6, 8.4, 100, False)

    a, b = evaluate_weighting(weights.route_weights.get("high_route_distance"),
                              weights.route_weights.get("low_route_distance"), distance_ratio, 1 - distance_ratio)
    rating += a
    total_weight_sum += b

    # Calculate City Ratings and Stability
    city_ratings = [city_ratings_data.get(city, 0) for city in route]

    average_city_rating = custom_sigmoid(mean(city_ratings), 53.3, 11.98, 100, False) if mean(city_ratings) > 5 else 0
    stddev_city_rating = 1 - (custom_sigmoid(std(city_ratings), 19.5, 3.85, 50, False) if std(city_ratings) > 4 else 0)

    a, b = evaluate_weighting(weights.route_weights.get("high_rated_cities"),
                              weights.route_weights.get("low_rated_cities"),
                              average_city_rating, 1 - average_city_rating)
    rating += a
    total_weight_sum += b

    a, b = evaluate_weighting(weights.route_weights.get("high_city_rating_stability"),
                              weights.route_weights.get("low_city_rating_stability"),
                              stddev_city_rating, 1 - stddev_city_rating)
    rating += a
    total_weight_sum += b

    # Calculate Flight Ratings
    flight_ratings = []
    for i in range(len(route) - 1):
        city_a = route[i]
        city_b = route[i + 1]
        flight_rating = route_ratings_data.get(city_a, {}).get(city_b, 0)
        flight_ratings.append(flight_rating)

    average_flight_rating = custom_sigmoid(mean(flight_ratings), 53.3, 11.98, 100, False) if mean(flight_ratings) > 5 else 0
    stddev_flight_rating = 1 - (custom_sigmoid(std(flight_ratings), 19.5, 3.85, 50, False) if std(flight_ratings) > 4 else 0)

    a, b = evaluate_weighting(weights.route_weights.get("high_rated_flights"),
                              weights.route_weights.get("low_rated_flights"),
                              average_flight_rating, 1 - average_flight_rating)
    rating += a
    total_weight_sum += b

    a, b = evaluate_weighting(weights.route_weights.get("high_flight_rating_stability"),
                              weights.route_weights.get("low_flight_rating_stability"),
                              stddev_flight_rating, 1 - stddev_flight_rating)
    rating += a
    total_weight_sum += b

    # Adjust Rating Based on Proximity to Start and End Airports
    start_distance = calculate_distance_cities(route[0], original_start)
    start_distance_score = custom_sigmoid(start_distance, 1 + radius_start / 1.42, 1 + radius_start / 12, 0, True)

    end_distance = calculate_distance_cities(route[-1], original_end)
    end_distance_score = custom_sigmoid(end_distance, 1 + radius_end / 1.42, 1 + radius_end / 12, 0, True)

    a, b = evaluate_weighting(weights.route_weights.get("near_start_airport"),
                              weights.route_weights.get("far_start_airport"),
                              start_distance_score, 1 - start_distance_score)
    rating += a
    total_weight_sum += b

    a, b = evaluate_weighting(weights.route_weights.get("near_end_airport"),
                              weights.route_weights.get("far_end_airport"),
                              end_distance_score, 1 - end_distance_score)
    rating += a
    total_weight_sum += b

    if total_weight_sum == 0:
        return 0
    else:
        rating = (rating / total_weight_sum) * 100
        return round(rating, 5)


if __name__ == '__main__':
    prec = retrieve_precomputed_data("tomsontomno", "template_test")
    w = Weights("tomsontomno", "template_test")

    print(rating_route(["Cologne", "Skopje", "Abu Dhabi", "Male"], w, "Cologne", "Male", 120, 0))
