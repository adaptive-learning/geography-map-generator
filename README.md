geography-map-generator
=======================

Generate maps for slepemapy.cz


## Initial setup

Install [kartograph.py](http://kartograph.org/docs/kartograph.py/#installing-kartograph-py)

Install [xmllint](http://xmlsoft.org/xmllint.html)

To download public shapefiles for already defined maps run
```
./fetch_shapefiles.py 
```

## Usage 

To get more info on how to generate maps run:

```
cd <path_to_your_local_git_repo>
./generate_maps.py
```

Some example usages:
```
./generate_maps.py all
./generate_maps.py world
./generate_maps.py continents Europe
./generate_maps.py continents Europe
./generate_maps.py states cz
./generate_maps.py states sk
./generate_maps.py states us
```
