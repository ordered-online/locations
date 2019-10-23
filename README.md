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

Following API Endpoints are supported:

### Find a location with`/locations/find/`
Finds a location to the given parameters.
Method: GET

|Parameter|Explanation|
|-|-|
|user_id|Search for locations by a specific user id.|
|name|Search for locations, whose names contain the given query (case insensitive).|
|category|Search for locations with a given category.|
|tag|Search for locations with a given tag.|

At least one of these parameters should be supplied. All parameters can be combined.
Results are limited to 100 locations.

Example name search with `curl`:
```
$ curl -i -X GET http://127.0.0.1:8000/locations/find/?name=asci

{ 
   "success":true,
   "response":[ 
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
      }
   ]
}
```

Example search for a given tag and a given category with `curl`:
```
$ curl -i -X GET http://127.0.0.1:8000/locations/find/?tag=calm&category=cafe

{ 
   "success":true,
   "response":[ 
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
      }
   ]
}
```

Failure Responses:
- [IncorrectAccessMethod](#IncorrectAccessMethod) if the service was accessed with any other method than specified.


### `/locations/find/nearby/`
Finds a location nearby.
Method: GET

|Parameter|Explanation|Mandatory|
|-|-|-|
|longitude|The longitude of the position to be searched.|yes|
|latitude|The loatitude of the position to be searched.|yes|
|radius|The radius in meters for results to be fetched.|no (Default is 10000m)|

Let's say you are at Helmholtzstraße and want to find locations within 1000m. Example name search with `curl`:
Results are limited to 100 locations.

Note the extra `distance` key which can be used for visual representation of the distance to the location.

```
$ curl -i -X GET http://127.0.0.1:8000/locations/find/nearby/\?latitude\=51.0282096\&longitude\=13.722814\&radius\=1000

{ 
   "success":true,
   "response":[ 
      { 
         "distance":370.0810107027033,
         "location":{ 
            "id":1,
            "name":"Studentencaf\u00e9 Ascii",
            "description":"Gem\u00fctliches Caf\u00e9 in der Fak. Informatik der TU Dresden.",
            "address":"N\u00f6thnitzer Str. 46, 01187 Dresden",
            "user_id":null,
            "latitude":"51.02508690",
            "longitude":"13.72100050",
            "website":null,
            "telephone":null,
            "categories":[ 
               { 
                  "name":"Cafe"
               }
            ],
            "tags":[ 
               { 
                  "name":"calm"
               },
               { 
                  "name":"inexpensive"
               },
               { 
                  "name":"insider"
               }
            ]
         }
      }
   ]
}
```

Failure Responses:
- [IncorrectAccessMethod](#IncorrectAccessMethod) if the service was accessed with any other method than specified.
- [ErroneousValue](#ErroneousValue) if the given coordinates or the given radius could not be parsed to floats.


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

Failure Responses:
- [IncorrectAccessMethod](#IncorrectAccessMethod) if the service was accessed with any other method than specified.
- [LocationNotFound](#LocationNotFound) if the requested location could not be found.


## Failure Responses

Following failure responses are supported:

### ErroneousValue

```
{ 
   "success":false,
   "reason":"erroneous_value"
}
```

### IncorrectAccessMethod

```
{ 
   "success":false,
   "reason":"incorrect_access_method"
}
```

### LocationNotFound

```
{ 
   "success":false,
   "reason":"location_not_found"
}
```


