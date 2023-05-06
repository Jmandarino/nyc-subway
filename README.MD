# NYC Subway API

## Getting started
This can be run with docker or without to run with docker please complete the following
- `docker-compose up -d --build`

On startup this container has a psql db, run database migrations as well as spins up a fast api
instance. 

### Connecting to the api
After the app is running please send requests to `http://localhost:8008`

## Documents and About
Fully typed and annotated swagger docs are located `http://localhost:8008/docs` please 
feel free to read for more information.


## Design Decision and Possible edge cases
### Typing and Validation
By default, these endpoints will validate data based on data types but also there are some
logical checks to make sure data entered is valid (e.g a station exists, the balanced entered, 
is positive). 

# PLEASE NOTE:
If you are trying to process a card on an entrance but the station you initialized didn't contain a fare. That station's fare is defaulted to free. If it has a connection
to another line the lowest price (0) will be used and subtracted 
from the balance
