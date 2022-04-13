# Jelly-Find (Media By Property)
query jellyfin to find media with given properties

### Examples
`-q avi,ass` match videos with the AVI container, match videos with ASS codec subtitles.

`-l 5` limit the results to 5 items per term (avi, ass).

`-v` prints out the total number of matches for a term.

`--movies` and `--shows` define which item types will be included. Doing just `--movies` instead of `--movies --shows` is faster since querying all the tv episodes can be slow.

`export JELLYFIN_URL="https://myurl" && export JELLYFIN_USERNAME="myusername" && export JELLYFIN_PASSWORD='mypassword'`

`python main.py -q avi,ass -l 5 -v --movies`

or

`python main.py -q avi,mp4,ass,mov_text -l 5 -v --movies --shows`
