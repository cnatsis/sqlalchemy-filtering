# SQLAlchemy filtering & sorting utility

## Purpose

This repository was developed to provide a simple JSON format interface to the [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)
query API to query on `json` SQL fields, which can be used by front-end applications to generate automatically SQL filtering queries
with minimum effort in the back-end service implementation.

## Features

Some of the `sqlalchemy-filtering` utility features include:

| Category  | Feature                             | PostgreSQL | MySQL      | SQLite |
|-----------|-------------------------------------|------------|------------|--------|
| Filtering | Ability to filter simple SQL fields | Yes        | Yes        | Yes    |
|           | Ability to filter `json` SQL fields | Yes        | Yes (Beta) | No     |
|           | Ability to filter join queries      | No         | No         | No     |
| Sorting   | Ability to sort simple SQL fields   | Yes        | Yes        | Yes    |
|           | Ability to sort `json` SQL fields   | Yes        | Yes (Beta) | No     |
|           | Ability to sort on joined fields    | No         | No         | No     |

## Usage

Given the following [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) models:

```python
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import functions

Base = declarative_base()


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    details = Column(JSONB)
    creation_date = Column(DateTime, nullable=False, server_default=functions.now())


class Ratings(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    creation_date = Column(DateTime, nullable=False, server_default=functions.now())
    movie_name = Column(String)
    rating = Column(Float)
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from test import models

engine = create_engine(
    'postgresql://postgres:password@localhost:5432/filter'
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

query = db.query(models.UserInfo)
```

Assuming we have records in the database with the following structure:
1. ID: `id` (type: _integer_)
2. Details: `details` (type: _json_)
```json
{
  "skin": "White",
  "extra": {
    "test": "value"
  },
  "gender": "Male",
  "height": 188,
  "last_name": "Walker",
  "first_name": "Paul",
  "user_details": [
    {
      "skill": "Fighting",
      "rating": 7
    },
    {
      "skill": "Driving",
      "rating": 10
    }
  ]
}
```
3. Creation date: `creation_date` (type: _timestamp_)

### Filtering

```python
# Case 1: Flat request on JSON column
obj = {
    "filter": [
        {
            ## (PostgreSQL) It returns all users that have skill 'Fighting' with rating 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            # "valueType": "jsonb",
            "value": "[{\"skill\":\"Fighting\",\"rating\":10}]",
        },
        {
            ## (PostgreSQL) It returns all users that have skill 'Fighting' and any rating (in any skill) with rating 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            "value": "[{\"skill\":\"Fighting\"},{\"rating\":10}]",
        }
    ]
}
```

```python
# Case2: Nested request in JSON nodes
obj = {
    "filter": [
        {
            "field": "details",
            "node": "extra",
            "value": {
                "field": "test",
                "operator": "==",
                "value": "value"
            }
        }
    ]
}
```

```python
from sqlalchemy_filtering.filter_util import filter_apply
from sqlalchemy_filtering.operators import SQLDialect
from sqlalchemy_filtering.validators import FilterRequest

from test import models

query = filter_apply(query=query, entity=models.UserInfo, obj=FilterRequest(obj), dialect=SQLDialect.POSTGRESQL)
```

#### Filtering operators

Filtering operators AND (`and_`), OR (`or_`) and NOT (`not_`) are supported and can be used all together. 

```python
obj3 = {
    "filter": {
        "not": [
            {
                "field": "movie_name",
                "operator": "==",
                "value": "The Dark Knight"
            },
            {
                "field": "rating",
                "operator": "==",
                "value": 7
            }
        ]

    }
}
```

### Sorting

```python
# Case 1: Sort request on JSON column
obj = {
    "sort": [
        {
            "field": "details",
            "node": "height",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}
```

```python
# Case 2: Sort request on inner JSON node column
obj = {
    "sort": [
        {
            "field": "details",
            "node": "extra.test",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}
```

```python
# Case 3: Sort request on simple column
obj = {
    "sort": [
        {
            "field": "creation_date",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}
```

```python
from sqlalchemy_filtering.sort_util import sort_apply
from sqlalchemy_filtering.validators import SortRequest

from test import models

query = sort_apply(query=query, entity=models.UserInfo, obj=SortRequest(obj))
```

## Versions tested

| System     | Version        |
|------------|----------------|
| PostgreSQL | 9.2, 12.7      |
| MySQL      | 8.0.20, 8.0.27 |
| SQLite     | 3.37           |
| SQLAlchemy | 1.4.25         |