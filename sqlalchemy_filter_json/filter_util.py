from sqlalchemy import Numeric
from sqlalchemy.sql.elements import BinaryExpression

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
    if obj.filter is None:
        return query

    for f_obj in obj.filter:
        root_node = f_obj.node

        jsonb_field = f_obj.json_field
        if f_obj.node is None:
            jsonb_node = f_obj.json_field
        else:
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
            if jsonb_field == jsonb_node:
                stmt = getattr(entity, jsonb_field)
            else:
                stmt = getattr(entity, jsonb_field)[jsonb_node]
        else:
            stmt = getattr(entity, jsonb_field)
            for n in jsonb_node.split('.'):
                stmt = stmt[n]

        # Cast fields
        stmt = _cast_statement(stmt, f_obj)

        # Apply operator
        stmt = f_obj.operator.execute(left=stmt, right=values)

        # Add filter to query object
        query = query.filter(stmt)
    return query


def _cast_statement(statement, obj: Filter = None):
    values = obj.value

    # TODO
    # if plain field (check with validator), 'return statement'
    # jsonb_field = obj["json_field"]

    if type(statement) == BinaryExpression.__name__:
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
