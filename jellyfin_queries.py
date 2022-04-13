from time import sleep


def get_movies(client=None):
    if client is None:
        return []

    params = {
        'Recursive': True,
        'includeItemTypes': (
            "Movie"
        ),
        'SortBy': 'DateCreated,SortName,ProductionYear',
        'SortOrder': 'Ascending',
        'enableImages': False,
        'enableUserData': False,
        'Fields': (
            'MediaSources'
        ),
        #'Limit': 1
    }

    movies = []
    try:
        result = client.jellyfin.user_items(params=params)
        if 'Items' in result and result['Items']:
            for item in result['Items']:
                #print(item['Name'])
                if 'MediaSources' in item:
                    movies.append(item)
                    #print(item['MediaSources'])
    except BaseException as err:
        return []
    sleep(0.2)
    return movies

def get_shows(client=None):
    if client is None:
        return []

    shows = []

    try:
        result = client.jellyfin.user_items(params={
            'Recursive': True,
            'includeItemTypes': (
                "Series"
            ),
            'SortBy': 'DateCreated,SortName',
            'SortOrder': 'Descending',
            'enableImages': False,
            'enableUserData': False,
        })

        if 'Items' in result and result['Items']:
            sleep(0.2)
            return result['Items']
        else:
            return []
    except BaseException as err:
        return []
    return shows

def get_episodes(client=None, series=None, limit=50):
    if client is None or series is None:
        return []

    episodes = []

    try:
        result = client.jellyfin.shows("/%s/Episodes" % series['Id'], {
            'UserId': "{UserId}",
            'Fields': (
                'MediaSources'
            ),
            'Limit': limit
        })

        if 'Items' in result and result['Items']:
            for episode in result['Items']:
                episode['SeriesName'] = series['Name']
            episodes = result['Items']
    except BaseException as err:
        return []
    sleep(0.2)
    return episodes