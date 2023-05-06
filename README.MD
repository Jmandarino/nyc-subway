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
### Archecture / Technologies
- Python
- Postgres SQL
- Fast API
- Sql Alchemy / Alembic
- Docker 
- Pytest
- Python Black/isort (formatting)


### Typing and Validation
By default, these endpoints will validate data based on data types but also there are some
logical checks to make sure data entered is valid (e.g a station exists, the balanced entered, 
is positive). 

## Example API routes

### Creating a new Trainline

**POST /train-line**
Body:
```json

{
  "stations": ["Spring", "West 4th", "14th", "23rd"],
  "name": "E"
}
```
**POST /train-line**
```json
{
  "stations": ["Canal", "Houston", "Christopher", "14th"],
  "name": "1",
  "fare":2.75
}
```

### Get shortest path between 2 stations

After posting the above lines we will find the shortest path. Transfers are assumed to be free

**POST /route?origin=Houston&destination=23rd**

Returns
```json
{
	"route": [
		"Houston",
		"Christopher",
		"14th",
		"23rd"
	]
}
```


### Credit Card

POST /card

number - unique identification of the card

amount - the amount of money to be added to the pre-paid card

returns confirmation of the card creation

If the card already exists, the amount should be added to the balance of the card.


**POST /card**

```json
{
  "number": "1234",
  "amount": 10.0
}
```
