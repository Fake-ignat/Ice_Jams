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
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        data = [row for row in reader][1:]
    return data


def load_json_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
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
    epoch_ms_time = (utc_time - dt.datetime(1970, 1, 1)).total_seconds() * 1000
    return [int(epoch_ms_time)]


def create_jams_popup_text(vals, str_date, code_status):
    name = vals['name']
    loc = vals['loc']
    river = vals['river']

    params = {
        'Дата': ".".join(str_date.split('-')[::-1]),
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


def create_floods_popup_text(params):
    popup_text = "".join(
        [
            f'{k:>20}: {v}\n'
            for k, v in params.items() if v
        ])

    return f"<pre>{popup_text}</pre>"


def ts_gJSON_params(name, times, popup_text, iconstyle):
    return {'tooltip': name,
            'popup': popup_text,
            'times': times,
            'icon': 'circle',
            'iconstyle': iconstyle
            }


def get_floods_iconstyle(homes, lands):
    if homes:
        fill_color = '#ff0000'
        radius = int(homes ** 0.5) if homes > 32 else 5
        if homes > 1000:
            radius = 25
    else:
        fill_color = '#ffff00'
        radius = int(lands ** 0.4) if lands > 100 else 5
        if lands > 1000:
            radius = 25
    return {
            'color': '#000000',
            'fill': True,
            'fillColor': fill_color,
            'fillOpacity': 0.7,
            'radius': radius
            }


class CustomGeoJSONMaker():
    def __init__(self, csv_locations_fname, KSVO_fname, save_gJSON_fname):

        self.save_gJSON_fname = save_gJSON_fname

        self.features = []
        self.id_storage = {}
        self.KSVO_data = sorted(load_csv_data(KSVO_fname), key=lambda line: (line[1], line[0]))
        
        
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
            id = line[1]
            name = line[2]
            river = line[5]
            lat, lon = map(float, (line[3], line[4]))

            self.id_storage[id] = dict(name=name,
                                       loc=[lat, lon],
                                       river=river)

    def get_locations_vals(self, id):
        # if len(id) < 5:
        #     for prefix in range(10):
        #         id = f'{prefix}{id}'
        #         if id in self.ids:
        #             break
        if id not in self.ids:
            return
        return self.id_storage[id]

    def extract_jams_data(self):
        for i, line in enumerate(self.KSVO_data):
            str_date = line[0]
            times = epoch_ms_time(str_date)
            code_status = ','.join(line[2:])

            id = line[1]
            vals = self.get_locations_vals(id)

            if not vals:
                continue

            name = vals['name']
            loc = vals['loc']

            popup_text = create_jams_popup_text(vals, str_date, code_status)
            params = ts_gJSON_params(name, times, popup_text, self.iconstyle)
            self.features.append(create_point_feature(loc, params))

            for delta in range(1, 4):
                fading_date = dt.datetime.strptime(str_date, "%Y-%m-%d") + dt.timedelta(days=delta)
                day_plus = fading_date.strftime("%Y-%m-%d")

                if i + delta < len(self.KSVO_data):
                    next_date, next_id = self.KSVO_data[i + delta][0:2]
                    if day_plus == next_date and id == next_id:
                        break
                    # print('NEXT', next_date, next_id)

                # print(day_plus, id)

                plus_times = epoch_ms_time(day_plus)
                plus_popup_text = create_jams_popup_text(vals, str_date, code_status)
                fading_iconstyle = {**self.iconstyle,
                                    **{
                                        'fillOpacity': 0.5,
                                        'opacity': 0.0,
                                        'radius': 5
                                    }}

                plus_params = ts_gJSON_params(name, plus_times, plus_popup_text, fading_iconstyle)
                self.features.append(create_point_feature(loc, plus_params))

    def extract_flood_data(self, json_fname):
        floods = load_json_data(json_fname)
        for region, districts in floods.items():
            for district, vals in districts.items():
                for place in vals:
                    try:
                        params = place['params']
                        loc = place["location"]
                        if not loc:
                            continue
                        name = place["нас. пункт"]
                        str_date = params["начало подтопления"]
                        
                        self.add_flood_feature(str_date, name, params, loc)
                        
                        if "конец подтопления" in params:
                            end_date = params["конец подтопления"]
                            # print('start_date ', str_date)
                            # print('end_date ', end_date)
                            if not end_date:
                                continue
                            
                            period = self.get_dates_period(str_date, end_date)
                            if period:
                                for day in period:
                                    self.add_flood_feature(day, name, params, loc)    
                            
                    except Exception as e:
                        print(e)
                        # print(f'{region} {district} {place}')

    def add_flood_feature(self, str_date, name, params, loc):
        
        homes = params['дома']
        lands = params['приусад. участки']
        params = {**{"нас.пункт": name}, **params}
        
        times = epoch_ms_time(str_date, '%d.%m.%Y')
        floods_iconstyle = get_floods_iconstyle(homes, lands)
        popup_text = create_floods_popup_text(params)

        gj_params = ts_gJSON_params(name, times, popup_text, floods_iconstyle)

        self.features.append(create_point_feature(loc, gj_params))
        
    def get_dates_period(self, start_date, end_date):
        period = []
        d0 = dt.datetime.strptime(start_date, '%d.%m.%Y')
        d1 = dt.datetime.strptime(end_date, '%d.%m.%Y')
        if d1 < d0:
            return
        delta = (d1-d0).days
        for i in range(1, delta):
            new_date = d0 + dt.timedelta(days=i)
            str_new_date = new_date.strftime('%d.%m.%Y')
            period.append(str_new_date)
        return period
            
        
    

if __name__ == '__main__':
    CSV_location_fname = '../csv/id - координаты.csv'
    SAVE_GJSON_fname = '../geo/ice_jams.geojson'
    KSVO_fname = '../csv/КСВО 11-12.csv'

    cgj_maker = CustomGeoJSONMaker(CSV_location_fname, KSVO_fname, SAVE_GJSON_fname)
    cgj_maker.extract_jams_data()

    cgj_maker.save_geo()
