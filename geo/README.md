# geo
The geo harvester is designed to pull various types of interesting geo specific strings from OSM.

```
usage: Query geo data [-h] [-r R] [-b] [-p] [-i] [-e] [-a] [-m] [-n] [-w] [-c] [-v] [-o O] query

positional arguments:
  query       Query to determine the location

optional arguments:
  -h, --help  show this help message and exit
  -r R        Query road names and set a granularity between 1-8
  -b          Query barriers and boundaries
  -p          Query historic and place
  -i          Query craft and office
  -e          Query infrastructure
  -a          Query shops, leisure, sport and amenities
  -m          Query man_made and buildings
  -n          Query natural and geological
  -w          Query water and waterways
  -c          Query everything
  -v          Verbose output, polutes stdout
  -o O        Output file

```

