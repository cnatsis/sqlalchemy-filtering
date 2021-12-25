from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_filter_json.filter_util import filter_apply
from sqlalchemy_filter_json.sort_util import sort_apply
from sqlalchemy_filter_json.validators import FilterRequest, SortRequest
from test import models2
from test.session import init_db, destroy_db, get_db

obj = {
    "filter": [
        {
            ## (PostgreSQL) It works and returns all users that have skill Fighting with rank 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            "valueType": "jsonb",
            "value": "[{\"skill\":\"Fighting\",\"rating\":10}]",
        }
        ,
        {
            ## (PostgreSQL) It works and returns all users that have skill Fighting and any rating (in any skill) with rank 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            "valueType": "jsonb",
            "value": "[{\"skill\":\"Fighting\"},{\"rating\":10}]",
        }
        # ,
        # {
        #     "field": "details",
        #     "node": "user_details",
        #     "value": {
        #             "json_field": "details",
        #             "node": "rating",
        #             "operator": ">",
        #             "value": 7.2
        #         }
        # }
        # ,
        # {
        #     "field": "details",
        #     "node": "user_details",
        #     "operator": ">",
        #     "value": 7.2,
        # }
        # {
        #     "field": "user_details",
        #     "node": "rating",
        #     "operator": "@>",
        #     "valueType": "jsonb",
        #     "value": "[{\"Column 1\":\"Test\"}]",
        # }
        # ,
        # {
        #     "field": "demographics",
        #     "node": "patient_details5",
        #     "operator": ">",
        #     "value": 8,
        # }
    ]
    ,
    "sort": [
        {
            "field": "details",
            "node": "user_details",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}

obj2 = {
    "filter": [
        {
            ## (PostgreSQL) It works and returns all users that have skill Fighting with rank 10
            "field": "movie_name",
            "operator": "like",
            "value": "%Dark%",
        }
    ],
    "sort": [
        {
            "field": "rating",
            # "node": "nested.field1",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}

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
    },
    "sort": [
        {
            "field": "rating",
            # "node": "nested.field1",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}

engine = create_engine(
    'postgresql://postgres:password@localhost:5432/filter',
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == '__main__':
    # destroy_db()

    # init_db()

    db = SessionLocal()

    query = db.query(models2.UserInfo)
    query = filter_apply(query=query, entity=models2.UserInfo, obj=FilterRequest(obj))
    query = sort_apply(query=query, entity=models2.UserInfo, obj=SortRequest(obj))

    # query = db.query(models2.Ratings)
    # query = filter_apply(query=query, entity=models2.Ratings, obj=FilterRequest(obj3))
    # query = sort_apply(query=query, entity=models2.Ratings, obj=SortRequest(obj3))

    print(models2.compile_query_postgres(query))
    # print("-------------")
    res = query.all()
    for r in res:
        print(dict(r.__dict__))
