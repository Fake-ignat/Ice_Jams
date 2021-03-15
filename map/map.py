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
    # data = []
    # with open('../csv/jams.csv', 'r', encoding='utf-8') as f:
    #     reader = csv.reader(f, delimiter=',')
    #     data = [row for row in reader]
    # my_map = MyMap(data)
    # my_map.save_map('../map/Заторы на реках.html')

    ice_jams = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "MultiPoint",
                    "coordinates": [ [80.53,  59.04] ]
                },
                "properties": {
                    "tooltip": "\u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a (\u0413\u041f \u043f\u0440\u0438 \u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a \u041c) - \u0440. \u041e\u0431\u044c",
                    "popup": "<pre>           \u0414\u0430\u0442\u0430: 28.04.2015\n      \u0413\u0438\u0434\u0440\u043e\u043f\u043e\u0441\u0442: \u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a (\u0413\u041f \u043f\u0440\u0438 \u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a \u041c) - \u0440. \u041e\u0431\u044c\n           \u0420\u0435\u043a\u0430: \u0440. \u041e\u0431\u044c\n           \u041a\u0421\u0412\u041e: [11]\n</pre>",
                    "times": [
                        1435708800000.0
                    ],
                    "icon": "circle",
                    "iconstyle": {
                        "color": "#000000",
                        "fill": True,
                        "fillColor": "#09042C",
                        "fillOpacity": 0.8,
                        "radius": 10
                    }
                }
            },
            {
            "type": "Feature",
            "geometry": {
                "type": "MultiPoint",
                "coordinates": [
                    [
                        59.04,
                        80.53
                    ],
                    [
                        59.04,
                        80.53
                    ],
                    [
                        59.04,
                        80.53
                    ]
                ]
            },
            "properties": {
                "name": "10022",
                "params": {
                    "\u0414\u0430\u0442\u0430": "28.04.2015",
                    "\u0413\u0438\u0434\u0440\u043e\u043f\u043e\u0441\u0442": "\u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a (\u0413\u041f \u043f\u0440\u0438 \u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a \u041c) - \u0440. \u041e\u0431\u044c",
                    "\u0420\u0435\u043a\u0430": "\u0440. \u041e\u0431\u044c",
                    "\u041a\u0421\u0412\u041e": "[11]"
                },
                "popup": "<pre>           \u0414\u0430\u0442\u0430: 28.04.2015\n      \u0413\u0438\u0434\u0440\u043e\u043f\u043e\u0441\u0442: \u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a (\u0413\u041f \u043f\u0440\u0438 \u041a\u0430\u0440\u0433\u0430\u0441\u043e\u043a \u041c) - \u0440. \u041e\u0431\u044c\n           \u0420\u0435\u043a\u0430: \u0440. \u041e\u0431\u044c\n           \u041a\u0421\u0412\u041e: [11]\n</pre>",
                "times": [
                        1430265600000, 1430352000000, 1430438400000
                ],
                "icon": "circle",
                "iconstyle": {
                    "color": "#000000",
                    "fill": True,
                    "fillColor": "#09042C",
                    "fillOpacity": 0.5,
                    "radius": 5,
                    "opacity": 0.0
                }
            }
        }
        ]
    }
        
    my_map = MyMap(ice_jams)
    my_map.save_map('map/Test.html')