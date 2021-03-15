from geo.geo_maker import CustomGeoJSONMaker
from geo.geo_filter import GeoFilter
from map.map import MyMap
import sys
import geojson
sys.path.append('.')


def load_geojson(filename):
    with open(filename, 'r') as f:
        data = geojson.load(f)
    return data["features"]

def save_geojson(filename, data):
        collection = {"type": "FeatureCollection", "features": data}
        with open(filename, 'w') as f:
            geojson.dump(collection, f)
            
def merge_geojson(g1_fname, g2_fname, save_name):
    g1 = load_geojson(g1_fname)
    g2 = load_geojson(g2_fname)
    g = g1 + g2
    print(len(g2))
    # save_geojson(save_name, g)

CSV_location_fname = 'csv/id - координаты.csv'
SAVE_GJSON_fname = 'geo/ice_jams.geojson' # 'geo/floods.geojson'  
KSVO_fname = 'csv/КСВО 11-12.csv'

floods_2013 = 'storage/floods/geo 2013.json'
floods_2014 = 'storage/floods/geo 2014.json'
floods_2015 = 'storage/floods/geo 2015.json'
floods_2016 = 'storage/floods/geo 2016.json'
floods_2017 = 'storage/floods/geo 2017.json'
floods_2018 = 'storage/floods/geo 2018.json'
floods_2019 = 'storage/floods/geo 2019.json'
floods_2020 = 'storage/floods/geo 2020.json'
floods_winter_17_20 = 'storage/floods/geo_winter_17_20.json'

jams_iconstyle = {
                'color': '#000000',
                'fill': True,
                'fillColor': '#09042C',
                'fillOpacity': 0.8,
                'radius': 10
            }

# cgj_maker = CustomGeoJSONMaker(CSV_location_fname, KSVO_fname, SAVE_GJSON_fname)
# cgj_maker.set_iconstyle(jams_iconstyle)
# cgj_maker.extract_jams_data()
# cgj_maker.save_geo()

# cgj_maker.save_gJSON_fname = SAVE_GJSON_fname = 'geo/floods.geojson'
# cgj_maker.features = []

# cgj_maker.extract_flood_data(floods_2013)
# cgj_maker.extract_flood_data(floods_2014)
# cgj_maker.extract_flood_data(floods_2015)
# cgj_maker.extract_flood_data(floods_2016)
# cgj_maker.extract_flood_data(floods_2017)
# cgj_maker.extract_flood_data(floods_2018)
# cgj_maker.extract_flood_data(floods_2019)
# cgj_maker.extract_flood_data(floods_2020)
# cgj_maker.extract_flood_data(floods_winter_17_20)
# cgj_maker.save_geo()

# ice_jams = {}
# with open(SAVE_GJSON_fname, 'r') as f:
#     ice_jams = geojson.loads(f.read())



# my_map = MyMap(ice_jams)
# my_map.save_map('map/Заторы на реках.html')

# jams_fname = 'geo/ice_jams.geojson'
# floods_fname = 'geo/floods.geojson'

# geo_filter = GeoFilter(jams_fname, floods_fname)
# geo_filter.filter_by_timeborder()
# geo_filter.filter_by_jams_times()
# geo_filter.filter_by_distance()
# # geo_filter.save_filtered_geojson('geo/filtered_floods.geojson')
# geo_filter.get_unique_floods('geo/filtered_floods.geojson', 'geo/unique_filtered_floods.geojson')
# geo_filter.get_unique_floods_by_time('geo/unique_filtered_floods.geojson', 'geo/total_filtered_floods.geojson')

g1_fname = 'geo/ice_jams.geojson'
g2_fname = 'geo/total_filtered_floods.geojson'
save_name = 'geo/filtered_flood_jams.geojson'
merge_geojson(g1_fname, g2_fname, save_name)

# ice_jams = {}
# with open(save_name, 'r') as f:
#     ice_jams = geojson.load(f)
# my_map = MyMap(ice_jams)
# my_map.save_map('map/Заторы подтопления.html')

# floods_fname = 'geo/filtered_floods.geojson'
# geo_filter2 = GeoFilter(jams_fname, floods_fname, 50)
# geo_filter2.filter_by_timeborder()
# geo_filter2.filter_by_jams_times()
# geo_filter2.filter_by_distance()
# geo_filter2.save_filtered_geojson('geo/filtered_floods_50.geojson')
# geo_filter2.get_unique_floods('geo/filtered_floods_50.geojson', 'geo/unique_filtered_floods_50.geojson')
