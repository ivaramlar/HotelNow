#encoding:utf-8

from math import sqrt

# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared_items
    si = {}
    for item in prefs[person1]: 
        if item in prefs[person2]: si[item] = 1

        # if they have no ratings in common, return 0
        if len(si) == 0: return 0

        # Add up the squares of all the differences
        sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) 
                    for item in prefs[person1] if item in prefs[person2]])
        
        return 1 / (1 + sum_of_squares)

# Returns the Pearson correlation coefficient for p1 and p2
def sim_pearson(prefs, p1, p2):
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1]: 
        if item in prefs[p2]: si[item] = 1

    # if they are no ratings in common, return 0
    if len(si) == 0: return 0

    # Sum calculations
    n = len(si)

    # Sums of all the preferences
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # Sums of the squares
    sum1Sq = sum([pow(prefs[p1][it], 2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it], 2) for it in si])	

    # Sum of the products
    pSum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # Calculate r (Pearson score)
    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0

    r = num / den

    return r

# Returns the best matches for person from the prefs dictionary. 
# Number of results and similarity function are optional params.
def topMatches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other) 
                for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

# Gets recommendations for a person by using a weighted average of every other user's rankings
def getRecommendations(prefs, person, similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person: continue
        sim = similarity(prefs, person, other)
        # ignore scores of zero or lower
        if sim <= 0: continue
        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # Create the normalized list
    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
    
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    # Create a dictionary of items showing which other items they
    # are most similar to.
    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        if c % 100 == 0: print ("%d / %d" % (c, len(itemPrefs)))
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, itemMatch, user):
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():
        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:
            print (item2)
            # Ignore if this user has already rated this item
            if item2 in userRatings: continue
            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating
            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    try:
        rankings = [(score / totalSim[item], item) for item, score in scores.items()]
    except ZeroDivisionError:
        rankings = []

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

def cosine_similarity(vec1, vec2):
    # Calculate dot product
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    # Calculate magnitudes of vectors
    magnitude1 = sqrt(sum(v1 ** 2 for v1 in vec1))
    magnitude2 = sqrt(sum(v2 ** 2 for v2 in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0  # Handle division by zero
    # Calculate cosine similarity
    return dot_product / (magnitude1 * magnitude2)


def recommend_hotels(hotel_data, reference_hotel, top_n=3):
    """
    Recommend hotels based on similarity to a reference hotel.
    """
    recommendations = []

    for hotel in hotel_data:
        if hotel["id"] != reference_hotel["id"]:  # Skip the reference hotel itself
            print("Calculating similarity between:", reference_hotel, "and", hotel)

            try:
                # Extract feature vectors for both hotels
                features1 = [
                    float(reference_hotel["precio"]),
                    float(reference_hotel["surface"]),
                    int(reference_hotel["bathrooms"]),
                    int(reference_hotel["rooms"]),
                    int(reference_hotel["tipo_encoded"]),
                ]
                features2 = [
                    float(hotel["precio"]),
                    float(hotel["surface"]),
                    int(hotel["bathrooms"]),
                    int(hotel["rooms"]),
                    int(hotel["tipo_encoded"]),
                ]

                # Calculate similarity
                similarity = cosine_similarity(features1, features2)
                recommendations.append((hotel, similarity))
            except Exception as e:
                print(f"Error calculating similarity: {e}")

    # Sort recommendations by similarity score (descending)
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    # Return top-N hotels
    return [rec[0] for rec in recommendations[:top_n]]


def recommend_cars(car_data, reference_car, top_n=5):
    """
    Recommend cars based on similarity to a reference car.

    Args:
        car_data (list of dict): List of cars with their features.
        reference_car (dict): The reference car for similarity comparison.
        top_n (int): Number of top recommendations to return.

    Returns:
        list of dict: Sorted list of recommended cars.
    """
    recommendations = []

    for car in car_data:
        if car["id"] != reference_car["id"]:  # Skip the reference car itself
            try:
                # Extract feature vectors
                features1 = [
                    float(reference_car["precio"]),
                    int(reference_car["fecha"]),
                    int(reference_car["kilometros"]),
                    int(reference_car["marca_encoded"]),
                ]
                features2 = [
                    float(car["precio"]),
                    int(car["fecha"]),
                    int(car["kilometros"]),
                    int(car["marca_encoded"]),
                ]

                # Calculate similarity
                similarity = cosine_similarity(features1, features2)
                recommendations.append((car, similarity))
            except Exception as e:
                print(f"Error calculating similarity: {e}")

    # Sort recommendations by similarity score (descending)
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    # Return top-N cars
    return [rec[0] for rec in recommendations[:top_n]]