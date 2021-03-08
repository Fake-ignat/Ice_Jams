from geo.geo_maker import CustomGeoJSONMaker
from map.map import MyMap
import sys
import geojson
sys.path.append('.')


CSV_location_fname = 'csv/id - координаты.csv'
SAVE_GJSON_fname = 'geo/ice_jams.geojson'
KSVO_fname = 'csv/КСВО 11-12.csv'

floods_2013 = 'storage/floods/geo 2013.json'
floods_2014 = 'storage/floods/geo 2014.json'
floods_2015 = 'storage/floods/geo 2015.json'

jams_iconstyle = {
                'color': '#000000',
                'fill': True,
                'fillColor': '#09042C',
                'fillOpacity': 0.8,
                'radius': 5
            }

cgj_maker = CustomGeoJSONMaker(CSV_location_fname, KSVO_fname, SAVE_GJSON_fname)
cgj_maker.set_iconstyle(jams_iconstyle)
cgj_maker.extract_jams_data()
cgj_maker.extract_flood_data(floods_2013)
cgj_maker.extract_flood_data(floods_2014)
cgj_maker.extract_flood_data(floods_2015)

cgj_maker.save_geo()


ice_jams = {}
with open('geo/ice_jams.geojson', 'r') as f:
    ice_jams = geojson.loads(f.read())



my_map = MyMap(ice_jams)
my_map.save_map('map/Заторы на реках.html')