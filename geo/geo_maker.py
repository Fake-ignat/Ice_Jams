import sys

sys.path.append('.')
import csv
from geojson import Feature, MultiPoint, FeatureCollection
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
                   geometry=MultiPoint(list(loc)),
                   properties=params)


def epoch_ms_time(str_date, format="%Y-%m-%d"):
    utc_time = dt.datetime.strptime(str_date, format)
    epoch_ms_time = (utc_time - dt.datetime(1970, 1, 1)).total_seconds() * 1000
    return int(epoch_ms_time)


def create_jams_popup_text(vals, str_date, code_status):
    name = vals['name']
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
    

    return f"<pre>{popup_text}</pre>", params


def create_floods_popup_text(params):
    popup_text = "".join(
        [
            f'{k:>20}: {v}\n'
            for k, v in params.items() if v
        ])

    return f"<pre>{popup_text}</pre>"


def ts_gJSON_params(name, times, popup_text, raw_params, iconstyle):
    return {'name': name,
            'params': raw_params,
            'popup': popup_text,
            'times': times,
            'icon': 'circle',
            'iconstyle': iconstyle
            }


def get_floods_iconstyle(homes, lands):
    fill_color = 'white'
    radius = 5
    if homes:
        fill_color = '#ff0000'
        radius = int(homes ** 0.5) if homes > 32 else 5
        if homes > 1000:
            radius = 25
    elif lands:
        fill_color = '#ffff00'
        radius = int(lands ** 0.5) if lands > 100 else 5
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
        self.times = []
        self.KSVO_data = sorted(load_csv_data(KSVO_fname), key=lambda line: (line[1], line[0]))
        self.KSVO_len = len(self.KSVO_data)
        
        
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
        
        if id not in self.ids:
            return
        return self.id_storage[id]

    def extract_jams_data(self):
        for i, line in enumerate(self.KSVO_data):
            str_date = line[0]
            times = [epoch_ms_time(str_date)]
            code_status = ','.join(line[2:])

            post_id = line[1]
            vals = self.get_locations_vals(post_id)

            if not vals:
                continue

            name = vals['name']
            loc = [vals['loc'][::-1]]

            popup_text, raw_params = create_jams_popup_text(vals, str_date, code_status)
            params = ts_gJSON_params(name, times, popup_text, raw_params, self.iconstyle)
            self.features.append(create_point_feature(loc, params))
            self.create_fading_points(i, name, post_id, str_date, loc, popup_text, raw_params)
                
    def create_fading_points(self, index, post_id, name, str_date, loc, popup_text, raw_params):
        fading_iconstyle = {**self.iconstyle,
                            **{'fillOpacity': 0.5, 'opacity': 0.0, 'radius': 5}}
        fading_times = []
        
        for delta in range(1, 4):
                fading_date = dt.datetime.strptime(str_date, "%Y-%m-%d") + dt.timedelta(days=delta)
                day_plus = fading_date.strftime("%Y-%m-%d")
                
                if index + delta < self.KSVO_len:
                    next_date, next_id = self.KSVO_data[index + delta][0:2]
                    
                    if day_plus == next_date and post_id == next_id:
                        break
                    
                fading_times.append(epoch_ms_time(day_plus))
          
        isShouldBeAdded = len(fading_times)
        
        if isShouldBeAdded:
            loc = loc * isShouldBeAdded
            plus_params = ts_gJSON_params(name, fading_times, popup_text, raw_params, fading_iconstyle)
            self.features.append(create_point_feature(loc, plus_params))


    def extract_flood_data(self, json_fname):
        floods = load_json_data(json_fname)
        for region, districts in floods.items():
            for district, vals in districts.items():
                for place in vals:
                    try:
                        params = place['params']
                        location = place["location"]
                        
                        if not location:
                            continue
                        
                        loc = [location[::-1]]
                        name = place["нас. пункт"]
                        str_date = params["начало подтопления"]
                        
                        flood_time = epoch_ms_time(str_date, '%d.%m.%Y')
                        assert isinstance(flood_time, int)
                        self.times.append(flood_time)
                        
                        
                        if "конец подтопления" in params:
                            end_date = params["конец подтопления"]
                            
                            if not end_date:
                                continue
                            
                            self.get_dates_period(str_date, end_date)
                            
                            
                        params['нас.пункт'] = name
                        params['МО'] = district
                        params['Субъект'] = region
                        
                        self.add_flood_feature(name, params, loc)
                        self.times = []
                        
                        
                    except Exception as e:
                        print(e)
                        print(f'{region} {district} {place}')

    def add_flood_feature(self, name, params, loc):
        
        homes, lands = None, None
        
        
        if 'дома' in params:
            homes = params['дома']
            
        if 'приусад. участки' in params:    
            lands = params['приусад. участки']
            
        
        floods_iconstyle = get_floods_iconstyle(homes, lands)
        popup_text = create_floods_popup_text(params)
        
        loc_multiplicator = len(self.times)
        if loc_multiplicator > 1:
            loc = loc * loc_multiplicator

        gj_params = ts_gJSON_params(name, self.times, popup_text, params, floods_iconstyle)

        self.features.append(create_point_feature(loc, gj_params))
        
    def get_dates_period(self, start_date, end_date):
        
        d0 = dt.datetime.strptime(start_date, '%d.%m.%Y')
        d1 = dt.datetime.strptime(end_date, '%d.%m.%Y')
        
        if d1 < d0:
            return
        
        delta = (d1-d0).days
        
        for i in range(1, delta):
            new_date = d0 + dt.timedelta(days=i)
            
            epoch_time = (new_date - dt.datetime(1970, 1, 1)).total_seconds() * 1000
            self.times.append(int(epoch_time))
            
        
    

# if __name__ == '__main__':
#     CSV_location_fname = '../csv/id - координаты.csv'
#     SAVE_GJSON_fname = '../geo/ice_jams.geojson'
#     KSVO_fname = '../csv/КСВО 11-12.csv'

#     cgj_maker = CustomGeoJSONMaker(CSV_location_fname, KSVO_fname, SAVE_GJSON_fname)
#     cgj_maker.extract_jams_data()

#     cgj_maker.save_geo()
