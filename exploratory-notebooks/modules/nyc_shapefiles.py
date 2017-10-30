"""Functions for working with NYC shapefiles."""

import fiona
import pyproj
from shapely.geometry import shape


def convert_geometry_to_gps(geometry, orig_proj):
    """Convert a geometry to GPS coordinates."""
    original = pyproj.Proj(orig_proj, preserve_units=True)
    destination = pyproj.Proj(init='epsg:4326')

    if geometry['type'] == 'Polygon':
        return shape({
            'type': 'Polygon',
            'coordinates': [
                [
                    pyproj.transform(original, destination, x, y)
                    for (x, y) in path
                ]
                for path in geometry['coordinates']
            ]
        })
    elif geometry['type'] == 'MultiPolygon':
        return shape({
            'type': 'MultiPolygon',
            'coordinates': [
                [
                    [
                        pyproj.transform(original, destination, x, y)
                        for (x, y) in path
                    ]
                    for path in polygon
                ]
                for polygon in geometry['coordinates']
            ]
        })
    else:
        return None


def read_nyc_shapefiles(path='../shapefiles/'):
    """Load the info from the NYC-provided shapefiles."""
    precincts = fiona.open(path + 'police_precincts/nypp.shp')
    tracts = fiona.open(path + 'census_tracts/nyct2010.shp')

    tract_dict = {}
    precinct_dict = {}

    for tract in tracts:
        tract_dict[tract['id']] = {
            'shape': convert_geometry_to_gps(
                tract['geometry'],
                tracts.crs
            ),
            'intersections': [],
            'properties': tract['properties']
        }

    for precinct in precincts:
        if precinct['id'] == '35':          # Bad shapefile
            precinct_geom = convert_geometry_to_gps(
                {
                    'type': 'MultiPolygon',
                    'coordinates': [precinct['geometry']['coordinates'][260]]
                },
                precincts.crs
            )
        elif precinct['id'] == '70':        # Bad shapefile
            precinct_geom = convert_geometry_to_gps({
                'type': 'MultiPolygon',
                'coordinates': [
                    precinct['geometry']['coordinates'][0],
                    precinct['geometry']['coordinates'][103]
                ]},
                precincts.crs
            )
        else:
            precinct_geom = convert_geometry_to_gps(
                precinct['geometry'],
                precincts.crs
            )

        precinct_dict[precinct['id']] = {
            'shape': precinct_geom,
            'intersections': [],
            'properties': precinct['properties']
        }

    for tract in tracts:
        if (int(tract['id']) % 50) == 0:
            print('Processing tract {0}'.format(tract['id']))
        for precinct in precincts:
            if tract_dict[tract['id']]['shape'].intersects(
                precinct_dict[precinct['id']]['shape']
            ):
                tract_dict[tract['id']]['intersections'].append(
                    precinct['id']
                )
                precinct_dict[precinct['id']]['intersections'].append(
                    tract['id']
                )
    return precinct_dict, tract_dict
