"""Functions for working with NYC shapefiles."""

from shapely.geometry import shape, mapping
import fiona
import pyproj
import json
import csv
import numpy as np
import pandas as pd
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
    """Make a dictionary to represent a tract or precinct.

    This function is for internal use.

    Parameters
    ----------
    shape_with_props : dict
        One of the entries in one of the NYC shapefiles
    geometry : GeoJSON
        The geometry to create the shape out of
    orig_projection : CRS
        The projection the file is stored in

    Returns
    -------
    entry : dict
        A dictionary with the information we want to keep from the shapefile
    """
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
    """Assign a census tract to the precincts it overlaps with.

    This function is for internal use. For a single census tract, it first
    calculates which precincts physically overlap with the census tract and how
    much area that overlap represents. It keeps a running total of the amount
    of area determined to overlap with the precincts (usually all or nearly all
    of the census tract, but occasionally slightly less.) Once all of the
    intersections with precincts have been determined, it then determines for
    each precinct what percentage of the census tract should be assigned to
    each precinct.

    In other words, if a census tract only overlaps with a single precinct,
    its population will be assigned 100 percent to that precinct. If the total
    area of the census tract is 10000, and its overlap with precinct A has
    area 6000, and its overlap with precinct B has area 4000, it will be
    assigned 60 percent to precinct A and 40 percent to precinct B. If the
    total area of the census tract is 10000, and it only overlaps with
    precincts C and D, and the area of overlap with precinct C is 6000 and the
    area of overlap with precinct with precinct D is 2000, it will be
    assigned 75 percent to precinct C and 25 percent to precinct D.

    Parameters
    ----------
    tract_id : string
        The id for the census tract in the NYC shapefile. This number doesn't
        correspond to anything else
    tract_entry : dict
        The dict entry whose 'intersections' key will be calculated
    precinct_dict : dict
        The dictionary of precincts created from the NYC shapefile. This
        dictionary will be modified by adding an entry to the 'intersections'
        key of every precinct that overlaps with the given census tract.
    """
    total_intersection_area = 0
    for precinct_id, precinct_entry in precinct_dict.items():
        if tract_entry['shape_orig'].intersects(
            precinct_entry['shape_orig']
        ):
            # Create a shapely object representing the intersection
            tract_precinct_intersection = \
                tract_entry['shape_orig'].intersection(
                    precinct_entry['shape_orig']
                )
            tract_precinct_intersection_area = \
                tract_precinct_intersection.area

            # Sometimes the intersection is a single point or a line.
            # Only proceed if the intersection is actually a two-dimensional
            # shape with positive area
            if tract_precinct_intersection_area > 0:
                total_intersection_area += tract_precinct_intersection_area

                tract_entry['intersections'][precinct_id] = {
                    'intersection_area_absolute':
                        tract_precinct_intersection_area
                }
                precinct_entry['intersections'][tract_id] = {}

    # Once the total area that intersects with police precincts is known,
    # calculate the percentage of the census tract assigned to each precinct
    tract_entry['total_intersection_area'] = \
        total_intersection_area
    for val in tract_entry['intersections'].values():
        val['intersection_area_percent_of_tract'] = \
            val['intersection_area_absolute'] / \
            total_intersection_area


def assign_precinct_to_tracts_by_pop(precinct_id, precinct_entry, tract_dict):
    """Assign a precinct to census tracts by population.

    This function is for internal use. The physical overlap with census tracts
    must already have been determined by the time this function is called.
    Given the list of census tracts that overlap with the given precinct, this
    function calculates the total population of the police precinct and then
    determines what percentage of the precinct belongs to each census tract.

    In other words, if 40 percent of census tract 1 has been assigned to the
    precinct and 100 percent of census tract 2 has been assigned to the
    precinct, and census tract 1 has population 5000 and census tract 2 has
    population 4000, then the precinct has total population 0.4*5000 + 1*4000
    = 6000. Therefore, 33 percent of the precinct will be determined to be in
    census tract 1 and 67 percent of the precinct will be determined to be in
    census tract 2.

    Parameters
    ----------
    precinct_id : string
        The id for the police precinct in the NYC shapefile. This number
        doesn't correspond to anything else; it is not the actual precinct
        number that the NYPD uses.
    precinct_entry : dict
        The dict entry whose 'intersections' key will be calculated
    tract_dict : dict
        The dictionary of census tracts created from the NYC shapefile and
        then modified by having intersections added with
        assign_tract_to_precincts_by_area().
    """
    total_precinct_pop = 0
    for tract_id, tract_val in precinct_entry['intersections'].items():
        # Get the percent of the census tract that's been assigned to this
        # precinct
        percent_in_precinct = \
            tract_dict[tract_id]['intersections'][precinct_id][
                'intersection_area_percent_of_tract'
            ]

        # Calculate the population to assign to this precinct
        ct_total_pop = tract_dict[tract_id]['census_info']['Population']
        precinct_pop = ct_total_pop * percent_in_precinct
        tract_val['population_assigned_to_precinct'] = precinct_pop

        # Add to the running total of population in the whole precinct
        total_precinct_pop += precinct_pop

    # Once the total precinct population is known, calculate the percentage
    # coming from each census tract
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
    """Load the info from the NYC-provided shapefiles.

    Parameters
    ----------
    shapefile_path : string, optional
        The folder containing the shapefiles from NYC OpenData
    census_path : string, optional
        The folder containing the files downloaded from American FactFinder
    verbose : bool, optional
        Whether or not to give a progress indicator as files are
        processed (function takes ~10-15 seconds to run total.)

    Returns
    -------
    precinct_dict : dict
        A dictionary of police precincts along with information about the
        precinct compiled from the shapefile and from the census info.

        Each key of this dictionary is an arbitrary ID that doesn't represent
        anything besides its ID in the NYC shapefile.
        Each value of the dictionary is itself a dictionary with the following
        keys:
        properties : An OrderedDict taken straight from the NYC shapefile.
            Among other things, this dict contains the actual precinct number
            that is used by the NYPD.
        shape_orig : A Shapely shape whose units are the original units (feet)
        shape_gps : A Shapely shape whose units are GPS coordinates
        intersections : A dict whose keys are the tract IDs and whose values
            are 'population_assigned_to_precinct' (number of people) and
            'population_percent_of_precinct' (which percent of the precinct
            is represented by this tract
        total_population : The total population that has been assigned to this
            precinct

    tract_dict : dict
        A dictionary of census tracts along with information about the tract
        compiled from the shapefile and from the census info.

        Each key of this dictionary is an arbitrary ID that doesn't represent
        anything besides its ID in the NYC shapefile.
        Each value of the dictionary is itself a dictionary with the following
        keys:
        properties : An OrderedDict taken straight from the NYC shapefile.
            Among other things, this dict contains the name of the borough
            and the census tract ID that can be used to cross-reference this
            file vs AFF data.
        shape_orig : A Shapely shape whose units are the original units (feet)
        shape_gps : A Shapely shape whose units are GPS coordinates
        intersections : A dict whose keys are the precinct IDs and whose values
            are 'intersection_area_absolute' (total area overlapping with
            the precinct in question) and
            'intersection_area_percent_of_tract' (which fraction of the census
            tract has been assigned to the precinct.)
        total_intersection_area : The total area of the census tract that
            actually overlaps with any police precincts
        census_info : A Pandas Series that is actually a pointer to a row in
            the census info table returned by the function.

    merged_census_info : DataFrame
        A Pandas DataFrame with index 'GEO.id' (a fully qualified census
        tract ID) and the following columns:
        'GEO.id2': a numeric version of the census tract
        'GEO.display-label': A string description of the census tract
        'Population': The census tract population
        'Median_Household_Income': The median household income
        'Percent_Bachelors_Degree': The percent of the population with
            a bachelors degree or above

    tract_df : DataFrame
        A Pandas DataFrame with the same information as merged_census_info,
        but whose index is the same arbitrary ID as for tract_dict.
    """
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


def create_dataframes(precinct_dict, tract_dict, merged_census_info):
    """Load the info from the NYC-provided shapefiles.

    Parameters
    ----------
    precinct_dict : dict
        A dictionary of police precincts along with information about the
        precinct compiled from the shapefile and from the census info.
        Should be in the format returned by read_nyc_shapefiles().

    tract_dict : dict
        A dictionary of census tracts along with information about the tract
        compiled from the shapefile and from the census info.
        Should be in the format returned by read_nyc_shapefiles().

    merged_census_info : DataFrame
        Should be in the format returned by read_nyc_shapefiles().

    Returns
    -------
    precinct_df : DataFrame
        A Pandas Dataframe with information aggregated from the census tracts.
        Contains the total population, the weighted average median household
        income, and the weighted average percent with bachelors degree.

    tract_df : DataFrame
        A Pandas DataFrame with the same information as merged_census_info,
        but whose index is the same arbitrary ID as for tract_dict.

    intersection_df : DataFrame
        A Pandas DataFrame with the intersections of census tracts
        and police precincts.
    """
    def weighted_average(x):
        return np.average(
            x,
            weights=intersection_df.loc[x.index, 'TractPopulationInPrecinct']
        )

    def add_weighted_average(column_name):
        precinct_df[column_name] = \
            intersection_df.dropna(
                subset=[column_name]
            ).groupby(
                'Precinct'
            ).agg(
                {column_name: weighted_average}
            )

    empty_tract_df = pd.DataFrame.from_dict(
        {k: v['census_info'].name
         for k, v in tract_dict.items()},
        orient='index')
    empty_tract_df.columns = [merged_census_info.index.name]
    tract_df = empty_tract_df.merge(
        merged_census_info,
        left_on=merged_census_info.index.name,
        right_index=True
    )
    tract_df.index.rename('TractShapefileID', inplace=True)

    empty_intersection_df = pd.DataFrame.from_records([
        (
            precinct_entry['properties']['Precinct'],
            tract_id,
            tract_entry['population_assigned_to_precinct'],
            tract_entry['population_percent_of_precinct']
        )
        for precinct_entry in precinct_dict.values()
        for tract_id, tract_entry in precinct_entry['intersections'].items()],
        columns=[
            'Precinct',
            'TractShapefileId',
            'TractPopulationInPrecinct',
            'PopulationPercentOfPrecinct'
        ]
    )
    intersection_df = empty_intersection_df.merge(
        tract_df,
        left_on='TractShapefileId',
        right_index=True
    )

    precinct_df = pd.DataFrame.from_dict(
        {v['properties']['Precinct']: k
         for k, v in precinct_dict.items()},
        orient='index'
    )
    precinct_df.columns = ['PrecinctShapefileID']
    precinct_df.index.rename('Precinct', inplace=True)
    precinct_df['Population'] = pd.Series(
        {entry['properties']['Precinct']: entry['total_population']
         for entry in precinct_dict.values()}
    )
    add_weighted_average('Median_Household_Income')
    add_weighted_average('Percent_Bachelors_Degree')

    return precinct_df, tract_df, intersection_df


def save_census_info(precinct_df, tract_df, intersection_df,
                     output_path='../precrime_data/'):
    """Save the dataframes as CSV."""
    precinct_df.to_csv(output_path + 'precinct_info.csv',
                       quoting=csv.QUOTE_NONNUMERIC)
    tract_df.to_csv(output_path + 'tract_info.csv',
                    quoting=csv.QUOTE_NONNUMERIC)
    intersection_df.to_csv(
        output_path + 'tract_precinct_intersection_info.csv',
        quoting=csv.QUOTE_NONNUMERIC
    )


def write_precinct_geojson(
    shape_dict,
    destination='../shinymap/nypd_precincts.geojson'
):
    """Write the precinct dict out as a geojson file.

    Parameters
    ----------
    shape_dict : dict
        A dict in the format created by read_nyc_shapefiles
    destination : string
        The name of the geojson file to create

    Returns
    -------
    None
    """
    def create_precinct_feature(key, val):
        feature = {
            'type': 'Feature',
            'id': key,
            'properties': {
                'Precinct': val['properties']['Precinct'],
                'Population': val['total_population']
            },
            'geometry': mapping(val['shape_gps'])
        }
        return feature

    def create_precinct_feature_collection(shape_dict):
        output_dict = {
            'type': 'FeatureCollection',
            'features': [create_precinct_feature(k, v)
                         for k, v in shape_dict.items()]
        }
        return output_dict

    feature_collection = create_precinct_feature_collection(shape_dict)
    with open(destination, 'w') as f:
        json.dump(feature_collection, f, indent=2)
