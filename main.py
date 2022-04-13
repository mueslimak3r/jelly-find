import os
import sys
import getopt
import jellyfin_queries

from jellyfin_api_client import jellyfin_login, jellyfin_logout

server_url = os.environ['JELLYFIN_URL'] if 'JELLYFIN_URL' in os.environ else ''
server_username = os.environ['JELLYFIN_USERNAME'] if 'JELLYFIN_USERNAME' in os.environ else ''
server_password = os.environ['JELLYFIN_PASSWORD'] if 'JELLYFIN_PASSWORD' in os.environ else ''


def check_media(media=[], queries=[], limit_per_query=1, verbose=False):
    if not media or not queries:
        return
    for item in media:
        if not 'MediaSources' in item:
            continue

        media_sources = item['MediaSources']
        for source in item['MediaSources']:
            if not 'MediaStreams' in source:
                continue
            for query in queries:
                if str(source['Container']).lower() == query['Name'].lower() and item['Id'] not in query['MatchedIds'] and item['Id'] not in query['IgnoredMatches']:
                    if len(query['MatchedIds']) < limit_per_query:
                        query['MatchedIds'].append(item['Id'])
                        query['Matches'].append(item)
                    elif verbose:
                        query['IgnoredMatches'].append(item['Id'])
            streams = source['MediaStreams']
            for stream in streams:
                for query in queries:
                    for key in stream:
                        if str(stream[key]).lower() == query['Name'].lower() and item['Id'] not in query['MatchedIds'] and item['Id'] not in query['IgnoredMatches']:
                            if len(query['MatchedIds']) < limit_per_query:
                                query['MatchedIds'].append(item['Id'])
                                query['Matches'].append(item)
                            elif verbose:
                                query['IgnoredMatches'].append(item['Id'])

def get_episodes(client):
    print('getting shows from jellyfin (limited to 50 episodes per show)')
    shows = jellyfin_queries.get_shows(client)
    if not shows:
        print('got 0 tv episodes from jellyfin')
        return []

    media = []
    for show in shows:
        episodes = jellyfin_queries.get_episodes(client, show)
        if episodes:
            media.extend(episodes)
    print('got %s tv episodes from jellyfin' % len(media))
    return media

def get_media(included_types=[]):
    if not included_types:
        return []
    client = jellyfin_login(server_url, server_username, server_password, "Find Media By Property")
    media = []
    if 'Movie' in included_types:
        print('getting movies from jellyfin')
        media.extend(jellyfin_queries.get_movies(client))
        print('got %s movies from jellyfin' % len(media))
    if 'Series' in included_types:
        media.extend(get_episodes(client))
    jellyfin_logout()
    return media

def main(argv):
    queries = []
    limit_per_query = 1
    verbose = False
    included_types = [] # movies, shows

    try:
        opts, args = getopt.getopt(argv, "hvq:l:", ["movies", "shows"])
    except getopt.GetoptError:
        print('main.py --movies --shows -q <mp4,ssa,ass> (terms to search for) -l <5> (items to return per search term)')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('main.py -q <mp4,ssa,ass> (terms to search for) -l <5> (items to return per search term)')
            sys.exit(2)
        elif opt == '-q':
            queries_list = arg.split(',')
            for q in queries_list:
                new_query = {}
                new_query['Name'] = q
                new_query['MatchedIds'] = []
                new_query['Matches'] = []
                new_query['IgnoredMatches'] = []
                queries.append(new_query)
        elif opt == '-l' and arg.isnumeric():
            limit_per_query = int(arg)
        elif opt == '-v':
            verbose = True
        elif opt == '--movies':
            included_types.append('Movie')
        elif opt == '--shows':
            included_types.append('Series')

    if server_url == '' or server_username == '' or server_password == '':
        print('you need to export env variables: JELLYFIN_URL, JELLYFIN_USERNAME, JELLYFIN_PASSWORD\n')
        sys.exit(2)

    if not queries:
        print('you need to provide at least one search term - eg: mp4 or mp4,mkv,srt')
        sys.exit(2)
    
    if not included_types:
        print('you need to provide at least one media type to include - eg: --movies and/or --shows')
        sys.exit(2)
    
    print('searching for terms %s with limit of %s matches per term' % (queries_list, limit_per_query))

    media = get_media(included_types)
    check_media(media, queries, limit_per_query, verbose)
    for query in queries:
        if not query['MatchedIds']:
            print('\nno results for %s' % query['Name'])
            continue
        print('\nitems matched for term [%s]:' % query['Name'])
        for match in query['Matches']:
            print('    Type: [%s] %sName: [%s]' % (match['Type'], ('Series: [%s]' % match['SeriesName']) if match['Type'] == 'Episode' else '', match['Name']))
        if query['IgnoredMatches']:
            print('    + %s addition matches' % len(query['IgnoredMatches']))

if __name__ == "__main__":
    main(sys.argv[1:])