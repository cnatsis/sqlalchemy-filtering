from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_filter_json import models
from sqlalchemy_filter_json.filter_util import filter_apply, sort_apply

engine = create_engine(
    'postgresql://postgres:password@localhost:5432/medical_forms',
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


obj = {
        "filter": [
            {
                "json_field": "demographics",
                "node": "patient_details10",
                "operator": "@>",
                "valueType": "jsonb",
                "values": "[{\"Column 1\":\"test\"}]",
            }
            # ,
            # {
            #     "json_field": "demographics",
            #     "node": "age",
            #     "operator": "==",
            #     "values": 80,
            # }
        ],
        # "sort": [
        #     {
        #         "json_field": "demographics",
        #         "node": "nested.field1",
        #         "direction": "asc",
        #         "nullsLast": True,
        #     }
        # ]
    }


if __name__ == '__main__':
    db = SessionLocal()

    query = db.query(models.Patient)

    query = filter_apply(query=query, entity=models.Patient, obj=obj)
    query = sort_apply(query=query, entity=models.Patient, obj=obj)

    from sqlalchemy.dialects import postgresql

    print(models.compile_query(query))
    print("-------------")
    res = query.all()
    print(res)
