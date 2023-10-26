from .sheets import load_properties, SPREADSHEET_ID
from .types import Spreadsheet, GeolocationData
from .targetting import get_best_sold_comps, DISTANCE_MULTPLIER, MAX_COMP_MILEAGE,get_neighborhood_3rd_quartile_price_sft
from math import sqrt

# TODO make the google sheets look up the neighborhood data instead of making the google api
# TODO maybe optiziming look ups by relying on already exisiting MI data

print("Loading solds...")
solds = load_properties(SPREADSHEET_ID, Spreadsheet.SOLD)
print("Loading actives...")
actives = load_properties(SPREADSHEET_ID, Spreadsheet.ACTIVE)



result =  get_best_sold_comps(actives[0],solds)

print("Getting best comps for first active")
for i, comp in enumerate(result.best_comps):
    print(f"#{i+1} - {comp.property.list_number}")

print(result.get_result_array())



