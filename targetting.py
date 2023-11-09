from math import sqrt
from heapq import nlargest
from datetime import datetime, timedelta
from .types import Property,PropertyResult,BestComps
from .sheets import MAX_COMP_MILEAGE, DISTANCE_MULTPLIER, SQUARE_FOOTAGE_MULTIPLIER, BATHROOM_MULTIPLIER,BEDROOM_MULTIPLIER
import numpy as np

cache = {}
def get_neighborhood_price_psqft_array(sold_listings: list, active: Property) -> list:

    if active.address.neighborhood in cache:
        return cache[active.address.neighborhood]


    price_per_sft_array = []

    for property in sold_listings:
        neighborhood_filter_passed = property.address.neighborhood == active.address.neighborhood
        distance_filter_passed = active.address.geo_data.get_distance_from_sold(property) < MAX_COMP_MILEAGE

        if neighborhood_filter_passed and distance_filter_passed:
            price_per_sft = property.get_price_psft()

            if price_per_sft != -1:
                price_per_sft_array.append(price_per_sft)


    cache[active.address.neighborhood] = price_per_sft_array
    return price_per_sft_array

def get_neighborhood_3rd_quartile_price_sft(active_property: Property, solds: list[Property]):
    neighborhood_price_psqft_array = get_neighborhood_price_psqft_array(solds, active_property)

    if not neighborhood_price_psqft_array:
        return 0

    third_quartile_price = np.percentile(neighborhood_price_psqft_array, 75)

    return third_quartile_price

# In our import sheet for our input data we can create a match function in order to 

def get_sold_property_score(active: Property, current_sold: Property, solds: list[Property]):

    if active.address.neighborhood != current_sold.address.neighborhood:
        return PropertyResult(0,Property());

    if active.address.geo_data.get_distance_from_sold(current_sold) > MAX_COMP_MILEAGE:
        return PropertyResult(0,Property());

    third_quartile_price = get_neighborhood_3rd_quartile_price_sft(active,solds)

    if current_sold.get_price_psft() < third_quartile_price:
        return PropertyResult(0,Property());


    if current_sold.status_dates.sold and current_sold.status_dates.sold <= (datetime.now() - timedelta(days=365)):
        print(f"Property {current_sold.list_number} too old")
        return PropertyResult(0,Property());


    distance_score = DISTANCE_MULTPLIER * ((1 - (sqrt((active.address.geo_data.latitude - current_sold.address.geo_data.latitude) ** 2 + \
            (active.address.geo_data.longitude  - current_sold.address.geo_data.longitude) ** 2 ))) * 100)

    sqft_value = abs(current_sold.attribs.square_footage - active.attribs.square_footage)

    result = (
        100 if sqft_value < 200 else
        85 if sqft_value < 350 else
        65 if sqft_value < 500 else
        0)

    sqft_score = SQUARE_FOOTAGE_MULTIPLIER * result

    try:
        bedroom_score = BEDROOM_MULTIPLIER * (100 - (abs(active.attribs.bedrooms - current_sold.attribs.bedrooms) / active.attribs.bedrooms * 25))
    except ZeroDivisionError:
        bedroom_score = 0


    try:
        bathroom_score = BATHROOM_MULTIPLIER * (100 - (abs(active.attribs.get_bathroom_float() - current_sold.attribs.get_bathroom_float()) / active.attribs.get_bathroom_float() * 25))
    except ZeroDivisionError:
        bathroom_score = 0

    return PropertyResult(distance_score + sqft_score + bedroom_score + bathroom_score, current_sold)


def get_best_sold_comps(active : Property, solds : list[Property]):
    comp_scores = []

    for sold in solds:
        comp_scores.append(get_sold_property_score(active,sold, solds))

    return BestComps(active, nlargest(3,comp_scores), float(get_neighborhood_3rd_quartile_price_sft(active,solds)))
