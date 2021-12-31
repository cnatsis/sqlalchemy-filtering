from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_filtering.filter_util import filter_apply
from sqlalchemy_filtering.operators import SQLDialect
from sqlalchemy_filtering.sort_util import sort_apply
from sqlalchemy_filtering.validators import FilterRequest, SortRequest
from tests import models

obj = {
    "filter": [
        {
            ## (PostgreSQL) It works and returns all users that have skill Fighting with rank 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            # "valueType": "jsonb",
            "value": "[{\"skill\":\"Fighting\",\"rating\":10}]"
        }
        ,
        {
            ## (PostgreSQL) It works and returns all users that have skill Fighting with rank 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            # "valueType": "jsonb",
            "value": "[{\"skill\":\"Fighting\",\"rating\":10}]",
        }
        ,
        {
            ## (PostgreSQL) It works and returns all users that have skill Fighting and any rating (in any skill) with rank 10
            "field": "details",
            "node": "user_details",
            "operator": "@>",
            # "valueType": "jsonb",
            "value": "[{\"skill\":\"Fighting\"},{\"rating\":10}]",
        }
        # ,
        # {
        #     "field": "details",
        #     "node": "user_details",
        #     "value": {
        #             "field": "details",
        #             "node": "rating",
        #             "operator": ">",
        #             "value": 7.2
        #         }
        # },
        # {
        #     "field": "details",
        #     "node": "height",
        #     "operator": ">",
        #     "value": 176
        # }
        # {
        #     "field": "details",
        #     "node": "user_details",
        #     "value": {
        #         "field": "extra",
        #         "node": "test",
        #         "operator": "==",
        #         "value": "value"
        #     }
        # }
        # ,
        # {
        #     "field": "details",
        #     "node": "user_details",
        #     "value": {
        #         "field": "details",
        #         "node": "skill",
        #         "operator": "==",
        #         "value": "[{\"skill\":\"Fighting\",\"rating\":10}]"
        #     }
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
    ]
    ,
    "sort": [
        {
            "field": "details",
            "node": "height",
            "direction": "desc",
            "nullsLast": True
        }
    ]
}

obj2 = {
    "filter": [
        {
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

obj4 = {
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

engine = create_engine(
    'postgresql://postgres:password@localhost:5432/filter',
    # 'mysql+pymysql://root:@localhost:3306/filter',
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if __name__ == '__main__':

    db = SessionLocal()

    query = db.query(models.UserInfo)
    query = filter_apply(query=query, entity=models.UserInfo, obj=FilterRequest(obj), dialect=SQLDialect.POSTGRESQL)
    query = sort_apply(query=query, entity=models.UserInfo, obj=SortRequest(obj))

    # query = db.query(models.Ratings)
    # query = filter_apply(query=query, entity=models.Ratings, obj=FilterRequest(obj3))
    # query = sort_apply(query=query, entity=models.Ratings, obj=SortRequest(obj3))

    print(models.compile_query_postgres(query))
    print("-------------")
    res = query.all()
    for r in res:
        print(dict(r.__dict__))
