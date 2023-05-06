from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from .schema import Connection, Station, TrainLine


def create_line(session: Session, stations: List[str], name: str, cost: Decimal):
    """Creates a subway line based off a list of station names.

    This method will get or create each station and make a connection between the 2
    stations as well as appending a line to each.

    SqlAlchemy has a specific way of operating so new objects are required to be added while we go

    """
    trainline = session.query(TrainLine).filter(TrainLine.name == name).first()
    if trainline:
        raise ValueError(f"Train line with name {name} already exists")
    trainline = TrainLine(name=name, cost=cost)
    session.add(trainline)
    # we can test many small queries or 2 bigger ones (all values in list and all values missing)
    # query = session.query(TrainLine.name).outerjoin(TrainLine).filter(TrainLine.id.is_(None), TrainLine.name.in_(names))
    prev = 0
    for station in stations:
        db_station = session.query(Station).filter(Station.name == station).first()

        if not db_station:
            db_station = Station(name=station, cost=cost)
            session.add(db_station)
            session.commit()
        else:
            # cost in Station acts as a cache.
            db_station.cost = min(cost, db_station.cost)
        connection = Connection(
            from_station_id=prev,
            to_station_id=db_station.id,
            distance=1,
            line=trainline.id,
        )
        rev_connection = Connection(
            from_station_id=db_station.id,
            to_station_id=prev,
            distance=1,
            line=trainline.id,
        )

        prev = db_station.id

        session.add(connection)
        session.add(rev_connection)
        session.commit()
    session.commit()
    return trainline.name


def find_routes(session: Session, origin: str, destination: str):
    """Find routes based of recusive SQL"""
    from sqlalchemy import text

    cte = text(
        f"""WITH RECURSIVE
                path (station_id, cost, path, depth, line) AS (
            SELECT
              s.id,
              0,
              CAST(s.name AS varchar(2000)),
              0,
              CAST('' AS varchar(2000))
            FROM
              stations s
            WHERE
              s.name = '{origin}' and s.name<> 'EOL'
            UNION ALL
            SELECT
              l.to_station_id,
              p.cost + l.distance,
              CONCAT_WS(',', p.path, s.name)::varchar(2000),
              p.depth + 1,
              CONCAT_WS(',', p.line, l.line)::varchar(2000)
            FROM
              path p
              JOIN connections l ON p.station_id = l.from_station_id
              JOIN stations s ON l.to_station_id = s.id
            WHERE
              s.name != ALL(string_to_array(p.path, ','))
              AND p.depth < 75
          )
            SELECT
              path.path,
              path.cost,
              path.line
            FROM
              path
              JOIN stations s ON path.station_id = s.id
            WHERE
              s.name = '{destination}' and s.name<> 'EOL'
            ORDER BY
              path.cost
            LIMIT 1
"""
    )
    result = session.execute(cte).fetchone()
    if result:
        path, cost, line = result
        return path
    raise ValueError(
        f"Route not found for origin: {origin} to destination: {destination}"
    )


def find_routes_py(session: Session, origin, destination):
    """Applies Dijkstra's algo to find the shortest path. if the path doesn't exist this
    will raise a ValueError.

    The work is done mainly in python and Stations are represented as ids for mos
    of the process instead of getting their names.

    At the end we map station id's to their name
    """
    from sqlalchemy import select

    from .graph import Graph

    # stores mapping id-> name and name->id
    subway_map = {}
    subways = select(Station.__table__)

    for _id, name, _ in session.execute(subways):
        subway_map[_id] = name
        subway_map[name] = _id

    for point in (origin, destination):
        if point not in subway_map:
            raise ValueError(f"Can't find Station: {point} in system")

    # EOL station is used as a helper station for the recursive function. We might not
    # need it going forward but we can filter it out for now
    stmt = select(Connection.__table__).where(
        Connection.to_station_id != 0, Connection.from_station_id != 0
    )
    graph = Graph()
    for _, from_station, to_station, distance, line_id in session.execute(stmt):
        graph.add_node(to_station)
        graph.add_node(from_station)
        graph.add_edge(to_station, from_station, distance)

    graph.shortest_path(subway_map[origin])
    path = graph.get_path(subway_map[destination], subway_map)
    if len(path) <= 1:
        raise ValueError(
            f"Route not found for origin: {origin} to destination: {destination}"
        )
    return path
