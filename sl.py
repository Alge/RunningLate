import requests

from settings import *

def travel_planner(origin, dest):
    """Get trip data from origin to destination

    origin: tuple of (lat, long) coordinates
    dest: tuple of (lat, long) coordinates
    """
    response = requests.get('https://api.sl.se/api2/TravelplannerV3/trip.json',
            params = {
                'key': TRAVELPLANNER_KEY,
                'lang': 'en',
                'originCoordLat': origin[0],
                'originCoordLong': origin[1],
                'destCoordLat': dest[0],
                'destCoordLong': dest[1]
                })
    print(response.json())
