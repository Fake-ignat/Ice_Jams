import sys
from itertools import takewhile
from geojson import Feature, Point, FeatureCollection
sys.path.append('.')
from geojson import dump, load
import datetime as dt
from geopy.distance import geodesic
from geo.geo_maker import epoch_ms_time



class GeoFilter:
    def __init__(self, jams_fname, floods_fname, dist_border=100):
        self.filtered_floods = []
        self.jams = self.load_geojson(jams_fname)
        self.jams_times = self.get_jams_times()
        self.unique_jams_locs = []
        self.floods = self.load_geojson(floods_fname)
        self.time_border = epoch_ms_time('2019-01-01')
        self.dist_border = dist_border
        
    @staticmethod
    def load_geojson(filename):
        with open(filename, 'r') as f:
            data = load(f)
        return data["features"]
    
    def filter_by_timeborder(self):
        print("Количество всех точек",len(self.floods))
        
        for feature in self.floods:
            flood_time = feature["properties"]['times']
            
            if flood_time < self.time_border:
                self.filtered_floods.append(feature)
                
        print("Количество точек до 2019", len(self.filtered_floods))
        
    def get_jams_times(self):
        acc = set()
        
        for feature in self.jams:
            jam_time = feature["properties"]['times'][0]
            acc.add(jam_time)
            
        return acc
        
        
    def filter_by_jams_times(self):
        acc = []
        
        for feature in self.floods:
            flood_time = feature["properties"]['times'][0]
            
            if flood_time in self.jams_times:
                acc.append(feature)
                
        self.filtered_floods = acc
        
        print("Количество точек с подтоплениями", len(acc))
    
    @staticmethod    
    def dict_between_points(point1, point2):
        loc1 = point1["geometry"]["coordinates"][::-1]
        loc2 = point2["geometry"]["coordinates"][::-1]
        return geodesic(loc1, loc2).km
            
    def get_unique_jams_locations(self):
        locs = set()
        for jam in self.jams:
                loc = ",".join(map(str, jam["geometry"]["coordinates"][::-1]))
                if loc not in locs:
                    locs.add(loc)
                    self.unique_jams_locs.append(jam)
                    
        
    def filter_by_distance(self):
        self.get_unique_jams_locations()
        filtered_floods = []
        len_floods = len(self.filtered_floods)
        len_jams = len(self.unique_jams_locs)
        
        for i, flood in enumerate(self.filtered_floods):
            for j, jam in enumerate(self.unique_jams_locs):
                print(f'{i}/{len_floods} -- {j}/{len_jams}')
                dist = self.dict_between_points(jam, flood)
                if dist <= self.dist_border and dist not in filtered_floods:
                    filtered_floods.append(flood)
                    break
                
        self.filtered_floods = filtered_floods
        print(f"Количество точек в пределах {self.dist_border} км", len(self.filtered_floods))
        
    def save_filtered_geojson(self, filename):
        collection = FeatureCollection(self.filtered_floods)
        with open(filename, 'w') as f:
            dump(collection, f)
            
    def get_unique_floods(self,load_fname, filename):
        acc = []
        floods = self.load_geojson(load_fname)
        locs = set()
        for flood in floods:
            loc = ",".join(map(str, flood["geometry"]["coordinates"][::-1]))
            if loc not in locs:
                locs.add(loc)
                acc.append(flood)
        print(len(acc))
        
        collection = FeatureCollection(acc)
        with open(filename, 'w') as f:
            dump(collection, f)