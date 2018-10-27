import requests
from datetime import datetime
import json
import pprint

from settings import TRAVELPLANNER_KEY, LOCATION_LOOKUP_KEY
from pytz import timezone

stockholm = timezone("Europe/Stockholm")
utc = timezone("UTC")

def stockholm_to_utc(sl_time):
    localized = stockholm.localize(sl_time)
    return localized.astimezone(utc)

def travel_planner(origin, dest):
    """Get trip data from origin to destination

    origin: tuple of (lat, long) coordinates
    dest: tuple of (lat, long) coordinates
    """
    res = requests.get('https://api.sl.se/api2/TravelplannerV3/trip.json',
            params = {
                'key': TRAVELPLANNER_KEY,
                'lang': 'en',
                'originCoordLat': origin[0],
                'originCoordLong': origin[1],
                'destCoordLat': dest[0],
                'destCoordLong': dest[1]
                }).json()
    return _travel_planner_internal(res)

def travel_planner_recon(recon_id):
    """Get trip data again for an already fetched trip

    recon_id: the recon_id you got when you fetched the trip the first time
    """
    res = requests.get('https://api.sl.se/api2/TravelplannerV3/reconstruction.json',
            params = {
                'key': TRAVELPLANNER_KEY,
                'ctx': recon_id
                }).json()

    return _travel_planner_internal(res)

def _travel_planner_internal(res):
    if "Trip" not in res:
      if "ErrorDetails" in res:
        return json.dumps({"error":res["ErrorDetails"]})
      return False
    trip = res['Trip'][0]

    sprint_dist = 0
    sprint_duration = 0
    sprint_goal_coords = ()
    sprint_goal_name = ""
    sprint_goal_type = ""
    sprint_deadline_timetable = ""
    sprint_deadline_realtime = None
    sprint_done = False
    all_legs = []

    for leg in trip['LegList']['Leg']:
        if not sprint_done:
            if leg['type'] == 'WALK':
                sprint_dist += leg['dist']
                sprint_duration += int(leg['duration'][2:-1])
                sprint_goal = (leg['Destination']['lat'], leg['Destination']['lon'])
            else:
                sprint_done = True
                sprint_goal_name = leg['Origin']['name']
                sprint_goal_type = leg['Product']['name']

                sprint_deadline_timetable = stockholm_to_utc(datetime.fromisoformat(
                        leg['Origin']['date'] + " " + leg['Origin']['time']))
                if 'rtTime' in leg['Origin']:
                    sprint_deadline_realtime = stockholm_to_utc(datetime.fromisoformat(
                            leg['Origin']['rtDate'] + " " + leg['Origin']['rtTime']))

        all_legs.append({
            'from': leg['Origin']['name'],
            'departure_time': stockholm_to_utc(datetime.fromisoformat(
                    leg['Origin']['date'] + " " + leg['Origin']['time'])),
            'to': leg['Destination']['name'],
            'arrival_time': stockholm_to_utc(datetime.fromisoformat(
                    leg['Destination']['date'] + " " + leg['Destination']['time'])),
            'type': leg['Product']['catOut'].strip() if 'Product' in leg else leg['type'],
            'line': leg['Product']['name'] if 'Product' in leg else ''
            })

    result = {
            'sprint_distance': sprint_dist,
            'sprint_duration': sprint_duration,
            'sprint_goal_type': sprint_goal_type,
            'sprint_goal_lat': sprint_goal[0],
            'sprint_goal_long': sprint_goal[1],
            'sprint_goal_name': sprint_goal_name,
            'sprint_deadline_timetable': sprint_deadline_timetable,
            'sprint_deadline_realtime': sprint_deadline_realtime,
            'legs': all_legs,
            'recon_id': trip['ctxRecon']
        }
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(result)
    return result


def location_lookup(query):
    res = requests.get('https://api.sl.se/api2/typeahead.json',
            params={
                'key': LOCATION_LOOKUP_KEY,
                'searchstring': query,
                'stationsonly': 'false'
                }).json()
    result = []
    if 'ResponseData' not in res:
        return []
    for row in res['ResponseData']:
        result.append({
            'name': row['Name'],
            'site_id': row['SiteId'],
            'type': row['Type'],
            'lat': int(row['Y']) / 10**6,
            'long': int(row['X']) / 10**6
            })
    return result
