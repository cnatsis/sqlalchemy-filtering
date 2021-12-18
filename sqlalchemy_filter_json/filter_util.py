from sqlalchemy import Numeric, nullslast

from sqlalchemy_filter_json.operators import Operator
from sqlalchemy_filter_json.validators import FilterRequest, Filter


def filter_apply(query, entity, obj: FilterRequest = None):
    """
    Example object

    -- Simple request
    obj = {
        "filter": [
            {
                "json_field": "demographics",
                "node": "age",
                "operator": ">=",
                "value": 20,
            },
            {
                 "json_field": "demographics",
                 "node": "first_name",
                 "operator": "like",
                 "value": "%Test%",
            }
        ],
        "sort": [...]
    }

    -- Nested request
    obj = {
        "filter": [
            {
                "json_field": "demographics",
                "node": "nested",
                "value": {
                    "json_field": "demographics",
                    "node": "field1",
                    "operator": ">=",
                    "value": 20
                }
            }
        ],
        "sort": [...]
    }
    """
    for f_obj in obj.filter:
        # Hold the root node
        root_node = f_obj.node

        jsonb_field = f_obj.json_field
        jsonb_node = f_obj.node
        values = f_obj.value

        if type(values) is dict:
            # Cast nested object to `Filter` class
            new_values = Filter(values)
            new_values.node = root_node + '.' + new_values.node
            query_obj = {"filter": [new_values]}
            query = filter_apply(query, entity, FilterRequest(query_obj))
            continue

        # Get model field
        node_split = jsonb_node.split('.')
        if len(node_split) == 1 and type(values) is not dict:
            stmt = getattr(entity, jsonb_field)[jsonb_node]
        else:
            stmt = getattr(entity, jsonb_field)
            for n in jsonb_node.split('.'):
                stmt = stmt[n]

        # Cast fields
        stmt = cast_jsonb_statement(stmt, f_obj)

        # Apply operator
        stmt = f_obj.operator.execute(left=stmt, right=values)

        # Add filter to query object
        query = query.filter(stmt)
    return query


def sort_apply(query, entity, obj: dict = None):
    """
    Example object

    -- Simple request
    obj = {
        "filter": [...],
        "sort": [
            {
                "json_field": "demographics",
                "node": "age",
                "direction": "asc",
                "nullsLast": True,
            }
        ]
    }

    -- Nested request
    obj = {
        "filter": [...],
        "sort": [
            {
                "json_field": "demographics",
                "node": "nested.field1",
                "direction": "asc",
                "nullsLast": True,
            }
        ]
    }
    """
    if "sort" not in obj.keys():
        return query

    sort_obj = obj["sort"]
    if len(sort_obj) != 0:
        for sort_request in sort_obj:
            node_sort = sort_request["node"]
            sort_split = node_sort.split('.')
            if len(sort_split) == 0:
                sort_stmt = getattr(entity, sort_request["json_field"])[sort_request["node"]]
            else:
                sort_stmt = getattr(entity, sort_request["json_field"])
                for s in sort_split:
                    sort_stmt = sort_stmt[s]

            direction = sort_request["direction"]
            nulls_last = sort_request["nullsLast"]

            if direction is None or direction == "asc":
                sort_stmt = sort_stmt.asc()
            elif direction == "desc":
                sort_stmt = sort_stmt.desc()
            else:
                raise Exception('Invalid `{}` order by direction'.format(direction))

            if nulls_last is not None and nulls_last:
                sort_stmt = nullslast(sort_stmt)

            # Apply order by to query
            query = query.order_by(sort_stmt)
        return query


def cast_jsonb_statement(statement, obj: Filter = None):
    values = obj.value

    # TODO
    # if plain field (check with validator), 'return statement'
    # jsonb_field = obj["json_field"]

    value_type = type(values)
    if value_type is list:
        if len(values) != 0:
            element = type(values[0])
            if element in (float, int, complex):
                statement = statement.cast(Numeric)
            else:
                statement = statement.astext
        else:
            return statement
    elif value_type is str:
        if obj.valueType and obj.valueType == "jsonb":
            return statement
        else:
            statement = statement.astext
    elif value_type in (float, int, complex):
        statement = statement.cast(Numeric)
    return statement
