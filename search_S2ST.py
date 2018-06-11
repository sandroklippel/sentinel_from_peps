import requests
from sentinel_from_peps import ImageTile

def search_S2ST(lat,lon,radius=1000,identifier=None,tileid=None,startDate=None,completionDate=None,maxCloud=100,maxRecords=None):
    '''Search S2ST collection of PEPS (French mirror for Sentinel2 data)
    lat - Latitude expressed in decimal degrees (EPSG:4326) - should be used with lon 90 <= X >= -90
    lon - Longitude expressed in decimal degrees (EPSG:4326) - should be used with lat 180 <= X >= -180
    radius=1000 - Expressed in meters - should be used with lon and lat X > 1
    startDate - Beginning of the time slice of the search query. Format should follow RFC-3339
    completionDate - End of the time slice of the search query. Format should follow RFC-3339
    cloudCover - Cloud cover expressed in percent
    maxRecords=50 - Number of results returned per page (default 50) 500 <= X >=1
    c = search_S2ST(-25.627752647341822, -51.09637134324484,startDate='2017-04-01',completionDate='2017-06-11')
    '''

    def parse_peps_geojson(response_dict):
        '''parse dict from peps geojson
        return number of images and images catalog
        '''

        images = 0
        catalog = []
        if 'properties' in response_dict:
            if 'totalResults' in response_dict['properties']:
                images = response_dict['properties']['totalResults']
                if images > 0:
                    for feature in response_dict["features"]:
                        tile = ImageTile(feature["id"])
                        for key in feature["properties"].keys():
                            if feature["properties"][key] is not None:
                                tile.set_property(key,feature["properties"][key])
                        catalog.append(tile)
                    catalog.sort()
        return (images, catalog)

    # check parameters

    # assert -90 >= lat <= 90
    # assert -180 >= lon <= 180
    # assert radius >= 1
    # if startDate is not None:
    #     assert re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(|Z|[\+\-][0-9]{2}:[0-9]{2}))?$",startDate) 
    # if completionDate is not None:
    #     assert re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}(T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?(|Z|[\+\-][0-9]{2}:[0-9]{2}))?$",completionDate) 
    # # if cloudCover is not None:
    # #     assert 0 >= cloudCover <= 100
    # if maxRecords is not None:
    #     assert 1 >= maxRecords <= 500

    if identifier is not None:
        search_keys = {'identifier':identifier}
    elif tileid is not None:
        search_keys = {'tileid':tileid,'startDate':startDate,'completionDate':completionDate,'cloudCover':'[0,{0:d}]'.format(maxCloud),'maxRecords':maxRecords}
    else:
        search_keys = {'lat':lat,'lon':lon,'radius':radius,'startDate':startDate,'completionDate':completionDate,'cloudCover':'[0,{0:d}]'.format(maxCloud),'maxRecords':maxRecords}

    base_url = 'https://peps.cnes.fr/resto/api/collections/S2ST/search.json'

    r = requests.get(base_url, params=search_keys)

    print(r.url)

    r.raise_for_status()

    # parse peps_geojson

    response_dict = r.json()

    images, catalog = parse_peps_geojson(response_dict)
    
    if images > 0:
        print("Images found: {}".format(images))
        print("")
        for i in catalog:
            print(i)
    else:
        print("No images found")

    return catalog