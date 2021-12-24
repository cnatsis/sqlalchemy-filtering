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
                "field": "demographics",
                "node": "age",
                "operator": ">=",
                "value": 20,
            },
            {
                 "field": "demographics",
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
                "field": "demographics",
                "node": "nested",
                "value": {
                    "field": "demographics",
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

        field = f_obj.field
        if f_obj.node is None:
            field_node = f_obj.field
        else:
            field_node = f_obj.node
        values = f_obj.value

        if type(values) is dict:
            # Cast nested object to `Filter` class
            new_values = Filter(values)
            new_values.node = root_node + '.' + new_values.node
            query_obj = {"filter": [new_values]}
            query = filter_apply(query, entity, FilterRequest(query_obj))
            continue

        # Get model field
        node_split = field_node.split('.')
        if len(node_split) == 1 and type(values) is not dict:
            if field == field_node:
                stmt = getattr(entity, field)
            else:
                stmt = getattr(entity, field)[field_node]
        else:
            stmt = getattr(entity, field)
            for n in field_node.split('.'):
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
