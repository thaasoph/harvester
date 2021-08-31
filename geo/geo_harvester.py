from OSMPythonTools.overpass import Overpass, overpassQueryBuilder
from OSMPythonTools.nominatim import Nominatim
import argparse
import pprint
import sys

highway_roads = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential']
highway_link_roads = ['motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link']
highway_special = ['living_street', 'service', 'pedestrian', 'track', 'bus_guideway', 'escape', 'raceway', 'road', 'busway']
highway_paths = ['footway', 'bridleway', 'steps', 'corridor', 'path']

verbose_output = False

def searchStreets(searchArea, granularity):
    if verbose_output:
        print(f"Searching for streets in {searchArea.displayName()} with granularity {granularity}")
    highway_selectors = []

    if granularity <= 1:
        highway_selectors += highway_roads[:2]
    elif granularity == 2:
        highway_selectors += highway_roads[:3]
    elif granularity == 3:
        highway_selectors += highway_roads[:3]
        highway_selectors += highway_link_roads[:3]
    elif granularity == 4:
        highway_selectors += highway_roads[:5]
        highway_selectors += highway_link_roads
    elif granularity == 5:
        highway_selectors += highway_roads
        highway_selectors += highway_link_roads
    elif granularity == 6:
        highway_selectors += highway_roads
        highway_selectors += highway_link_roads
        highway_selectors += highway_special
    elif granularity == 7:
        highway_selectors += highway_roads
        highway_selectors += highway_link_roads
        highway_selectors += highway_special
        highway_selectors += highway_paths
    elif granularity >= 8:
        load_all = True

    selector_criteria = ['name']
    if load_all:
        selector_criteria.append('highway')
    else:
        highway_regex='|'.join(highway_selectors)
        selector_criteria.append(f'"highway"~"{highway_regex}"')

    query = overpassQueryBuilder(area=searchArea, elementType='way',selector=selector_criteria, out='body')
    overpass = Overpass()
    streets = overpass.query(query)
    street_names = set()
    for street in streets._elements:
        street_names.add(street.tags()['name'])
    if verbose_output:
        print(f"Found {len(street_names)} unique street names")

    return street_names

def searchForKey(searchArea, key):
    if verbose_output:
        print(f"Searching for {key} in {searchArea.displayName()}")

    selector_criteria = ['name', key]
    query = overpassQueryBuilder(area=searchArea, elementType='node',selector=selector_criteria, out='body')
    overpass = Overpass()
    result = overpass.query(query)
    entries = set()
    for result_entry in result._elements:
        entries.add(result_entry.tags()['name'])
    if verbose_output:
        print(f"Found {len(entries)} unique entries")

    return entries

def writeToOutput(output, result):
    for line in result:
        output.write("%s\n" % line)


def main(args):
    nominatim = Nominatim()
    searchArea = nominatim.query(args.query)
    if verbose_output:
        print(searchArea.displayName())
    output = args.o

    result = set()
    if args.c:
        writeToOutput(output, searchStreets(searchArea, 8))
    if args.r:
        writeToOutput(output, searchStreets(searchArea, args.s))
    if args.a or args.c:
        writeToOutput(output, searchForKey(searchArea, 'shop'))
        writeToOutput(output, searchForKey(searchArea, 'amenity'))
        writeToOutput(output, searchForKey(searchArea, 'leisure'))
        writeToOutput(output, searchForKey(searchArea, 'sport'))
    if args.b or args.c:
        writeToOutput(output, searchForKey(searchArea, 'barrier'))
        writeToOutput(output, searchForKey(searchArea, 'boundary'))
    if args.m or args.c:
        writeToOutput(output, searchForKey(searchArea, 'man_made'))
        writeToOutput(output, searchForKey(searchArea, 'building'))
    if args.i or args.c:
        writeToOutput(output, searchForKey(searchArea, 'craft'))
        writeToOutput(output, searchForKey(searchArea, 'office'))
    if args.e or args.c:
        writeToOutput(output, searchForKey(searchArea, 'emergency'))
        writeToOutput(output, searchForKey(searchArea, 'power'))
        writeToOutput(output, searchForKey(searchArea, 'public_transport'))
        writeToOutput(output, searchForKey(searchArea, 'railway'))
        writeToOutput(output, searchForKey(searchArea, 'telecom'))
    if args.n or args.c:
        writeToOutput(output, searchForKey(searchArea, 'geological'))
        writeToOutput(output, searchForKey(searchArea, 'natural'))
    if args.p or args.c:
        writeToOutput(output, searchForKey(searchArea, 'historic'))
        writeToOutput(output, searchForKey(searchArea, 'place'))
    if args.w or args.c:
        writeToOutput(output, searchForKey(searchArea, 'water'))
        writeToOutput(output, searchForKey(searchArea, 'waterway'))
    if verbose_output:
        print(f'Found a total of {len(result)} unique entries')



if __name__ == "__main__":
    parser = argparse.ArgumentParser("Query geo data")
    parser.add_argument('-r', type=int, help='Query roads names and set a granularity between 1-8')
    parser.add_argument('-b', action='store_true', help='Query barriers and boundaries')
    parser.add_argument('-p', action='store_true', help='Query historic and place')
    parser.add_argument('-i', action='store_true', help='Query craft and office')
    parser.add_argument('-e', action='store_true', help='Query infrastructure')
    parser.add_argument('-a', action='store_true', help='Query shops, leisure, sport and amenities')
    parser.add_argument('-m', action='store_true', help='Query man_made and buildings')
    parser.add_argument('-n', action='store_true', help='Query natural and geological')
    parser.add_argument('-w', action='store_true', help='Query water and waterways')
    parser.add_argument('-c', action='store_true', help='Query everything')
    parser.add_argument('-v', action='store_true', help='Verbose output, polutes stdout')
    parser.add_argument('-o', type=argparse.FileType('w',encoding="utf-8"), default=sys.stdout, help='Output file')
    parser.add_argument('query', nargs=1, help='Query to determine the location')

    args = parser.parse_args()
    verbose_output = args.v
    main(args)



