"""Functions for working with NYC shapefiles."""

from shapely.geometry import shape
import fiona
import pyproj
from .census_info import read_census_info, get_full_census_tract_id


def convert_geometry_to_gps(geometry, orig_projection):
    """Convert a geometry to GPS coordinates.

    Parameters
    ----------
    geometry : GeoJSON
        The geometry must have type 'Polygon' or 'MultiPolygon'.
    orig_projection : CRS
        The original projection that the file is stored in.

    Returns
    -------
    shape : a Shapely shape
        A shape whose points are in GPS units (long, lat)
    """
    original = pyproj.Proj(orig_projection, preserve_units=True)
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


def make_dict_entry(shape_with_props, geometry, orig_projection):
    """Make a dictionary to represent a tract or precinct."""
    entry = {
        'shape_orig': shape(geometry),
        'shape_gps': convert_geometry_to_gps(
            geometry,
            orig_projection
        ),
        'intersections': {},
        'properties': shape_with_props['properties']
    }
    return entry


def assign_tract_to_precincts_by_area(tract_id, tract_entry, precinct_dict):
    """Assign a census tract to the precincts it overlaps with."""
    total_intersection_area = 0
    for precinct_id, precinct_entry in precinct_dict.items():
        if tract_entry['shape_orig'].intersects(
            precinct_entry['shape_orig']
        ):
            tract_precinct_intersection = \
                tract_entry['shape_orig'].intersection(
                    precinct_entry['shape_orig']
                )
            tract_precinct_intersection_area = \
                tract_precinct_intersection.area

            if tract_precinct_intersection_area > 0:
                total_intersection_area += tract_precinct_intersection_area

                tract_entry['intersections'][precinct_id] = {
                    'intersection_area_absolute':
                        tract_precinct_intersection_area
                }
                precinct_entry['intersections'][tract_id] = {}
    tract_entry['total_intersection_area'] = \
        total_intersection_area
    for val in tract_entry['intersections'].values():
        val['intersection_area_percent_of_tract'] = \
            val['intersection_area_absolute'] / \
            total_intersection_area


def assign_precinct_to_tracts_by_pop(precinct_id, precinct_entry, tract_dict):
    """Assign a precinct to census tracts by population."""
    total_precinct_pop = 0
    for tract_id, tract_val in precinct_entry['intersections'].items():
        percent_in_precinct = \
            tract_dict[tract_id]['intersections'][precinct_id][
                'intersection_area_percent_of_tract'
            ]
        ct_total_pop = tract_dict[tract_id]['census_info']['Population']
        precinct_pop = ct_total_pop * percent_in_precinct
        tract_val['population_assigned_to_precinct'] = precinct_pop
        total_precinct_pop += precinct_pop

    precinct_entry['total_population'] = total_precinct_pop
    for tract_val in precinct_entry['intersections'].values():
        tract_val['population_percent_of_precinct'] = \
            tract_val['population_assigned_to_precinct'] / \
            total_precinct_pop


def read_nyc_shapefiles(
    shapefile_path='../shapefiles/',
    census_path='../census_info/',
    verbose=False
):
    """Load the info from the NYC-provided shapefiles."""
    merged_census_info = read_census_info(census_path)
    precincts = fiona.open(shapefile_path + 'police_precincts/nypp.shp')
    tracts = fiona.open(shapefile_path + 'census_tracts/nyct2010.shp')

    tract_dict = {}
    precinct_dict = {}

    for tract in tracts:
        tract_boro = tract['properties']['BoroName']
        tract_ct_id = tract['properties']['CT2010']
        if tract_boro == 'Staten Island' and tract_ct_id == '008900':
            # This census tract is some weird relic, population is zero
            # and the census tract is underwater.
            continue
        tract_dict[tract['id']] = make_dict_entry(
            tract,
            tract['geometry'],
            tracts.crs
        )
        tract_dict[tract['id']]['census_info'] = merged_census_info.loc[
            get_full_census_tract_id(tract_boro, tract_ct_id)
        ]

    for precinct in precincts:
        if precinct['id'] == '35':          # Bad shapefile
            precinct_geom = {
                'type': 'MultiPolygon',
                'coordinates': [precinct['geometry']['coordinates'][260]]
            }
        elif precinct['id'] == '70':        # Bad shapefile
            precinct_geom = {
                'type': 'MultiPolygon',
                'coordinates': [
                    precinct['geometry']['coordinates'][0],
                    precinct['geometry']['coordinates'][103]
                ]
            }
        else:
            precinct_geom = precinct['geometry']

        precinct_dict[precinct['id']] = make_dict_entry(
            precinct,
            precinct_geom,
            precincts.crs
        )

    for tract_id, tract_entry in tract_dict.items():
        if verbose and (int(tract_id) % 50) == 0:
            print('Processing tract {0}'.format(tract_id))
        assign_tract_to_precincts_by_area(
            tract_id,
            tract_entry,
            precinct_dict
        )

    for precinct_id, precinct_entry in precinct_dict.items():
        assign_precinct_to_tracts_by_pop(
            precinct_id,
            precinct_entry,
            tract_dict
        )

    return precinct_dict, tract_dict, merged_census_info
