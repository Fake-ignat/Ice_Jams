import sys

sys.path.append('.')
import csv
from geojson import Feature, Point, FeatureCollection, MultiPoint
from geojson import dump as geodump
import json
import datetime as dt


jams_iconstyle = {
                'color': '#000000',
                'fill': True,
                'fillColor': '#09042C',
                'radius': 5
            }


def load_csv_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        data = [row for row in reader][1:]
    return data


def save_JSON_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_point_feature(loc, params):
    return Feature(None,
                   geometry=Point(loc[::-1]),
                   properties=params)


def epoch_ms_time(str_date, format="%Y-%m-%d"):
    utc_time = dt.datetime.strptime(str_date, format)
    epoch_ms_time = (utc_time - dt.datetime(1970, 1, 1)).total_seconds() * 1000.0
    return [int(epoch_ms_time)]


def create_popup_text(vals, str_date, code_status):
    name = vals['name']
    loc = vals['loc']
    river = vals['river']

    params = {
        'Дата': str_date,
        'Гидропост': name,
        'Река': river,
        'КСВО': code_status
    }

    popup_text = "".join(
        [
            f'{k:>15}: {v}\n'
            for k, v in params.items() if v
        ]
    )

    return f"<pre>{popup_text}</pre>"


def ts_gJSON_params(name, times, popup_text, iconstyle):
    return {'tooltip': name,
            'popup': popup_text,
            'times': times,
            'icon': 'circle',
            'iconstyle': iconstyle
            }


class CustomGeoJSONMaker():
    def __init__(self, csv_locations_fname, KSVO_fname, save_gJSON_fname):

        self.save_gJSON_fname = save_gJSON_fname

        self.features = []
        self.id_storage = {}
        self.KSVO_data = load_csv_data(KSVO_fname)
        self.iconstyle = {}

        self.load_ids_to_storage(csv_locations_fname)
        self.ids = self.id_storage.keys()

    def set_iconstyle(self, iconstyle):
        self.iconstyle = iconstyle

    def save_geo(self):
        collection = FeatureCollection(self.features)
        with open(self.save_gJSON_fname, 'w') as g:
            geodump(collection, g)

    def load_ids_to_storage(self, filename):
        csv_data = load_csv_data(filename)

        for line in csv_data:
            id = line[0]
            name = line[2]
            river = line[5]
            lat, lon = map(float, (line[3], line[4]))

            self.id_storage[id] = dict(name=name,
                                       loc=[lat, lon],
                                       river=river)

    def get_locations_vals(self, id):
        if len(id) < 5:
            for prefix in range(10):
                id = f'{prefix}{id}'
                if id in self.ids:
                    break
        if id not in self.ids:
            return
        return self.id_storage[id]

    def extract_jams_data(self):
        for line in self.KSVO_data:
            str_date = line[0]
            times = epoch_ms_time(str_date)
            code_status = ','.join(line[2:])

            id = line[1]
            vals = self.get_locations_vals(id)

            if not vals:
                continue

            name = vals['name']
            loc = vals['loc']

            popup_text = create_popup_text(vals, str_date, code_status)

            params = ts_gJSON_params(name, times, popup_text, self.iconstyle)
            self.features.append(create_point_feature(loc, params))


if __name__ == '__main__':
    CSV_location_fname = '../csv/id - координаты.csv'
    SAVE_GJSON_fname = '../geo/ice_jams.geojson'
    KSVO_fname = '../csv/КСВО 11-12.csv'

    cgj_maker = CustomGeoJSONMaker(CSV_location_fname, KSVO_fname, SAVE_GJSON_fname)
    cgj_maker.extract_jams_data()
    cgj_maker.save_geo()
