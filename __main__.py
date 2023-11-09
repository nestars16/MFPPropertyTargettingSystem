from math import sqrt
from time import sleep
from flask import Flask
from .sheets import load_properties ,write_result_array, get_all_solds, clean_solds,append_solds_to_master
from .types import Spreadsheet 
from .targetting import get_best_sold_comps

# TODO make the google sheets look up the neighborhood data instead of making the google api
# TODO maybe optiziming look ups by relying on already exisiting MI data

app = Flask(__name__)

@app.route("/old_run", methods=["GET"])
def run_active_scores():
    print("Loading solds...")
    solds = load_properties(Spreadsheet.SOLD)
    print("Loading actives...")
    actives = load_properties(Spreadsheet.ACTIVE)

    results = []
    
    for i,active in enumerate(actives):
        print(f"Calculating best comps for active #{i}")
        results.append(get_best_sold_comps(active,solds))
    
    #print(result.get_result_array())

    write_result_array(results)

    return 'Ran sucessfully',200

@app.route("/run", methods=["GET"])
def run():
    print("Loading solds...")
    solds = get_all_solds()
    print("Solds loaded")
    append_solds_to_master()
    print("Solds appended to master")
    clean_solds()
    print("Solds sheet cleaned")
    print("Loading actives...")
    actives = load_properties(Spreadsheet.ACTIVE)

    results = []
    
    for i,active in enumerate(actives):
        print(f"Calculating best comps for active #{i}")
        results.append(get_best_sold_comps(active,solds))

    write_result_array(results)

    return 'Ran sucessfully',200

@app.route("/minimal_run", methods=["GET"])
def min_run():
    solds = get_all_solds()
    actives = load_properties(Spreadsheet.ACTIVE)

    results = []
    
    for i,active in enumerate(actives):
        print(f"Calculating best comps for active #{i}")
        results.append(get_best_sold_comps(active,solds))

    write_result_array(results)

    return 'Ran sucessfully',200

@app.route("/append_solds", methods=["GET"])
def append_solds():
    append_solds_to_master()
    return "Appended solds", 200

# Clean solds and filter
# Make dashboard pretty
# Host service

"""
1. Long Term is to create another 'scoring' system on top of the additional
scoring system to score comps, to granularly separate things like seller motivation
on top of projecting value

2. List price to ARV, then time on market
"""

if __name__ == '__main__':
    app.run(port=5000, debug=True)
