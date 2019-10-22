# ordered online locations service

This django based micro service manages all location (i.e., bars, restaurants, ...) related tasks.

## Technology Stack

- Python 3
- Django

## Quickstart

Make sure, that Python 3 and Django are installed. Run the server.
```
$ cd locations
$ python3 manage.py migrate
$ python3 manage.py runserver
```

If you want to prepopulate your database with some examples, run:
```
$ python3 manage.py load_data
```

## API Endpoints

Example response if unsuccessful:
```json
{
  "success": false
}
```

Following API Endpoints are supported:

### `/locations/find/`
Finds a location.
Method: GET

|Parameter|Explanation|
|-|-|
|user_id|Search for locations by a specific user id.|
|name|Search for locations, whose names contain the given query (case insensitive).|
|category|Search for locations with a given category.|
|tag|Search for locations with a given tag.|

At least one of these parameters should be supplied. All parameters can be combined.

Example name search with `curl`:
```
$ curl -i -X GET http://127.0.0.1:8000/locations/find/?name=asci

[ 
   { 
      "model":"locations.location",
      "pk":1,
      "fields":{ 
         "name":"Studentencaf\u00e9 Ascii",
         "description":"Gem\u00fctliches Caf\u00e9 in der Fak. Informatik der TU Dresden.",
         "address":"N\u00f6thnitzer Str. 46, 01187 Dresden",
         "user_id":null,
         "latitude":"51.02508690",
         "longitude":"13.72100050",
         "website":null,
         "telephone":null,
         "categories":[ 
            "Caf\u00e9"
         ],
         "tags":[ 
            "calm",
            "inexpensive",
            "insider"
         ]
      }
   }
]
```

Example search for a given tag and a given category with `curl`:
```
$ curl -i -X GET http://127.0.0.1:8000/locations/find/?tag=calm&category=cafe

[ 
   { 
      "model":"locations.location",
      "pk":1,
      "fields":{ 
         "name":"Studentencaf\u00e9 Ascii",
         "description":"Gem\u00fctliches Caf\u00e9 in der Fak. Informatik der TU Dresden.",
         "address":"N\u00f6thnitzer Str. 46, 01187 Dresden",
         "user_id":null,
         "latitude":"51.02508690",
         "longitude":"13.72100050",
         "website":null,
         "telephone":null,
         "categories":[ 
            "Caf\u00e9"
         ],
         "tags":[ 
            "calm",
            "inexpensive",
            "insider"
         ]
      }
   }
]
```

### `/locations/find/nearby/`
Finds a location nearby.
Method: GET

|Parameter|Explanation|Mandatory|
|-|-|-|
|longitude|The longitude of the position to be searched.|yes|
|latitude|The loatitude of the position to be searched.|yes|
|radius|The radius in meters for results to be fetched.|no (Default is 10000m)|

Let's say you are at Helmholtzstraße and want to find locations within 1000m. Example name search with `curl`:
```
$ curl -i -X GET http://127.0.0.1:8000/locations/find/nearby/?latitude=51.0282096&longitude=13.722814&radius=1000

[ 
   { 
      "model":"locations.location",
      "pk":1,
      "fields":{ 
         "name":"Studentencaf\u00e9 Ascii",
         "description":"Gem\u00fctliches Caf\u00e9 in der Fak. Informatik der TU Dresden.",
         "address":"N\u00f6thnitzer Str. 46, 01187 Dresden",
         "user_id":null,
         "latitude":"51.02508690",
         "longitude":"13.72100050",
         "website":null,
         "telephone":null,
         "categories":[ 
            "Cafe"
         ],
         "tags":[ 
            "calm",
            "inexpensive",
            "insider"
         ]
      }
   },
   { 
      "model":"locations.location",
      "pk":2,
      "fields":{ 
         "name":"Turtle Bay Dresden",
         "description":"Karibisches Restaurant in gem\u00fctlicher Atmosph\u00e4re mit Gerichten aus Trinidad, Jamaika und Martinique.",
         "address":"Kleine Br\u00fcdergasse, 01067 Dresden",
         "user_id":null,
         "latitude":"51.02508690",
         "longitude":"13.72100050",
         "website":null,
         "telephone":null,
         "categories":[ 
            "Bar",
            "Restaurant"
         ],
         "tags":[ 
            "caribbean",
            "dresden-for-friends",
            "popular"
         ]
      }
   }
]
```

### `/locations/<location_id>/`
Gets the requested location.
Methods: GET.

Example with `curl`: 

```
$ curl -i -X GET http://127.0.0.1:8000/locations/1/

[ 
   { 
      "model":"locations.location",
      "pk":1,
      "fields":{ 
         "name":"Studentencaf\u00e9 Ascii",
         "description":"Gem\u00fctliches Caf\u00e9 in der Fak. Informatik der TU Dresden.",
         "address":"N\u00f6thnitzer Str. 46, 01187 Dresden",
         "user_id":null,
         "latitude":"51.02508690",
         "longitude":"13.72100050",
         "website":null,
         "telephone":null,
         "categories":[ 
            "Caf\u00e9"
         ],
         "tags":[ 
            "calm",
            "inexpensive",
            "insider"
         ]
      }
   }
]
```



