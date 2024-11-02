"""
    APP ROUTES
    Routes for different app logic
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# IMPORTS ---------------
from flask import Blueprint, request, jsonify
import sys, os

# modules
from utilities.Navigator2 import Navigator, NavController
from tasks.JobsManager import localJobLoader


# BLUEPRINT ---------------
app_routes = Blueprint('app_routes', __name__)


# GLOBAL OBJECTS ---------------
global navigator
navigator = Navigator()


# APP ROUTES ---------------

"""
    ROUTE: /retrieve_jobs
    METHOD: GET
    DESCRIPTION: Retrieves all jobs from the navigator
    REQUEST FORMAT: {
        "filters": ["agency", "subject", "location"]
    }
"""
@app_routes.route('/retrieve_jobs', methods=['POST'])
def retrieve_jobs():

    # get request parameters
    params = request.json
    filters = params['filters']
    agencies = params['agencies']

    # first try local loading of jobs
    local_loader = localJobLoader()
    jobs = local_loader.load_jobs()


    # if local loading fails, load from the navigator
    if jobs is None:
        jobs = []
        for agency in agencies:
            # get the navigator for the agency
            nav_controller = NavController(agency, navigator)
            site_navigator = nav_controller.navigator

            jobs.extend(site_navigator.get_available_jobs())

        jobs = [job.serialize() for job in jobs]

        # save the jobs
        local_loader.save_jobs(jobs)


    return jsonify(jobs)


