from matplotlib import pyplot as plt
import geopandas as gpd
import openrouteservice as ors
from shapely.geometry import LineString, MultiLineString
import numpy as np
import pandas as pd
import json


class Route(object):

    def __init__(self, params=None, base_url=None, key=None, profile="foot-walking", fmt="geojson", file=None):
        """
        Initializes parameters and sends request to ORS server

        :param params: dict
        :param base_url: string
        """

        self.__dataframe = None
        self.__headers = headers = {"headers":{
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Content-Type': 'application/json; charset=utf-8'}}
        
        self.params = params
        self.base_url = base_url
        self.key = key
        self.profile =profile
        self.fmt = fmt
        
        if file is None:
            self.__json_response = self.request_route()
        else:
            self.load(file)


    def load(self, file):
        """
        Loads route from file
        """
        with open(file) as src:
            self.__json_response = json.load(src)
        
    def request_route(self):
        """
        Send route request to ORS server

        :param params: dict containing request parameters
        :param base_url: string of ORS base url
        :return: dict of ORS response
        """
        if self.base_url is not None:
            client = ors.Client(base_url=self.base_url)
        else:
            client = ors.Client(key=self.key)

        # Check if ors instance is running
        #if not client.request(url='/health', get_params={})["status"] == "ready":
        #    raise Exception("No connection to server.")
        # Send request
        try:
            return client.request(url="v2/directions/{}/{}".format(self.profile, self.fmt), post_json=self.params, requests_kwargs=self.__headers, get_params=[])
        except ors.exceptions.ApiError as e:
            raise ValueError(e.message)
        finally:
            del client

    @property
    def json_response(self):
        """
        Returns the ORS response as a dictionary
        :return: dict
        """
        return self.__json_response

    @property
    def route_options(self):
        """
        Number of route options 
        """
        return len(self.json_response["features"])
    
    def coordinates(self, option=0):
        """
        Returns the coordinates of the route from the ORS response
        :return: list of coordinates
        """
        return self.json_response['features'][option]['geometry']['coordinates']

    def extras(self, option=0):
        """
        Returns the extra information from the ORS response
        :return:
        """
        try:
            return self.json_response['features'][option]['properties']['extras']
        except:
            return None

    def values(self, criteria):
        """
        Returns the values for a certain criterion
        :param criterion: 'green', 'noise' or 'steepness'
        :return: values of criterion along route
        """
        return np.concatenate([np.repeat(v[2], v[1] - v[0]) for v in self.extras[criteria]['values']])

    def green_exposure(self):
        """
        Returns the overall exposure to greenness of the route
        :return: green exposure
        """
        summary = self.summary("green")
        return sum(summary["value"] * summary["distance"]) / summary["distance"].sum()

    def solar_exposure(self):
        """
        Returns the overall exposure to greenness of the route
        :return: green exposure
        """
        summary = self.summary("shadow")
        return sum(summary["value"] * summary["distance"]) / summary["distance"].sum()
    
    def steepness_exposure(self):
        """
        Returns the overall exposure to positive and negative steepness of the route
        :return: steepness exposure for negative and positive values
        """
        summary = self.summary("steepness")
        pos = []
        neg = []
        dist_Neg = []
        dist_Pos = []
        for o in range(len(summary["value"])):
            if summary["value"][o] > 0:
                pos.append(summary["value"][o])
                dist_Pos.append(summary["distance"][o])
            else:
                neg.append(summary["value"][o])
                dist_Neg.append(summary["distance"][o])

        if sum(dist_Neg) != 0:
            res2 = sum(np.array(neg) * np.array(dist_Neg)) / sum(dist_Neg)
        else:
            res2 = np.nan
        if sum(dist_Pos) != 0:
            res1 = sum(np.array(pos) * np.array(dist_Pos)) / sum(dist_Pos)
        else:
            res1 = np.nan
        return [res1, res2]

    def noise_exposure(self):
        """
        Returns the overall exposure to noise of the route
        :return: noise exposure
        """
        summary = self.summary("noise")
        return sum(summary["value"] * summary["distance"]) / summary["distance"].sum()

    def duration(self, option=0):
        """
        Returns the overall duration of the route
        :return: Duration
        """
        return self.json_response['features'][option]['properties']["summary"]['duration']

    def distance(self, option=0):
        """
        Returns the overall distance of the route
        :return: Distance
        """
        return self.json_response['features'][option]['properties']["summary"]['distance']

    def descent(self, option=0):
        """
        Returns the overall distance of the route
        :return: Distance
        """
        return self.json_response['features'][option]['properties']['descent']

    def ascent(self, option=0):
        """
        Returns the overall distance of the route
        :return: Distance
        """
        return self.json_response['features'][option]['properties']['ascent']
 
    def summary(self, criterion):
        """
        Returns the summary for a certain criterion of the ORS response as a pandas dataframe
        :param criterion: 'green', 'noise' or 'steepness'
        :return: Dataframe with summary
        """
        if criterion in self.extras.keys():
            return pd.DataFrame(self.extras[criterion]['summary'])
        else:
            raise ValueError("criterion '%s' does not exist.")

    def plot_summary(self, criterion):
        """
        Returns a bar plot of the summary for a certain criterion
        :param criterion: 'green', 'noise' or 'steepness'
        :return: Bar plot showing summary
        """
        summary = self.summary(criterion)
        return plt.bar(x=summary["value"], height=summary["amount"], color="green")

    def route_segments(self, option=0):
        """
        Returns segments of the route
        :return: list of LineStrings
        """
        coordinates = self.coordinates(option)
        n_segments = len(coordinates) - 1
        segments = []
        for i in range(0, n_segments):
            segments.append(LineString(coordinates[i:i + 2]))
        return segments

    # todo write test for this function
    def as_dataframe(self):
        """
        Converts the route and its extra information into a geopandas dataframe
        :return: GeoDataFrame with route information
        """
        if self.__dataframe is not None:
            return self.__dataframe
        else:
            route_geometries = [LineString(self.coordinates(option=opt)) for opt in range(0, self.route_options)]
            durations = [self.duration(option=opt) for opt in range(0, self.route_options)]
            distances = [self.distance(option=opt) for opt in range(0, self.route_options)]
            df = gpd.GeoDataFrame({"geometry": route_geometries, 
                                  "duration": durations,
                                  "distance": distances}, crs="epsg:4326")

            #if self.extras() is not None:

            #    for k in self.extras.keys():
            #        df[k] = self.values(k)

                # Dissolve line strings
            #    columns = list(df.columns.drop("geometry"))
            #    df = df.dissolve(by=columns, as_index=True).reset_index()
            #    df.geometry = df.geometry.apply(lambda x: MultiLineString([x]) if isinstance(x, LineString) else x)
                
        self.__dataframe = df
        return self.__dataframe

    def to_geojson(self, outfile, driver):
        """
        Writes the route to a geojson file
        :param outfile: Path to output file as string
        :return:
        """
        self.as_dataframe().to_file(outfile, driver=driver)

    def plot(self, *args, **kwargs):
        """
        Plots the route on a map
        :param args:
        :param kwargs:
        :return: plotted route
        """
        return self.as_dataframe().plot(*args, **kwargs)
    
    def to_file(self, outfile):
        """
        Writes the whole response to file. 
        """
        with open(outfile, "w") as dst:
            json.dump(self.json_response, dst, indent=4)
            
    
        

