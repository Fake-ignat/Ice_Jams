import sys

sys.path.append('.')
import folium
import json
import csv
from folium.plugins import TimestampedGeoJson

sys.path.append('.')


class MyMap:
    START_LOC = [55.75, 67.6167]
    ARCGIS_TILE = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

    def __init__(self, jams_geojson):
        self.map = folium.Map(location=self.START_LOC, zoom_start=4, dragging=True)
        self.jams_geojson = jams_geojson
        self.add_jams()
        self.add_tileLayers()

    def add_jams(self):
        james = TimestampedGeoJson(
            data=self.jams_geojson,
            period='P1D',
            duration='P1D',
            date_options='DD MMMM YYYY'
        )
        self.map.add_child(james)

    def save_map(self, filename):
        self.map.save(filename)

    def creat_arcGis_tileLayer(self):
        AG_TileLayer = folium.raster_layers.TileLayer(tiles=self.ARCGIS_TILE,
                                                      attr="ArcGIs",
                                                      name="ArcGis Спутник")
        AG_TileLayer.add_to(self.map)

    def add_tileLayers(self):
        self.creat_arcGis_tileLayer()
        folium.TileLayer('Stamen Terrain').add_to(self.map)
        folium.TileLayer('Stamen Toner').add_to(self.map)
        folium.TileLayer('Stamen Watercolor').add_to(self.map)
        folium.LayerControl().add_to(self.map)


if __name__ == '__main__':
    data = []
    with open('../csv/jams.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        data = [row for row in reader]
    my_map = MyMap(data)
    my_map.save_map('../map/Заторы на реках.html')
