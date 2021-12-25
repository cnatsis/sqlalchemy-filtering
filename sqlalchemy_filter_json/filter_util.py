from sqlalchemy import Numeric
from sqlalchemy.sql.elements import BinaryExpression

from sqlalchemy_filter_json.operators import FilterOperator
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

    --- Simple request with operators
    obj = {
        "filter": [
            "and": [
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
            ]
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
    exps = []
    if obj.filter is None:
        return query

    for key_operator in obj.filter.keys():
        for f_obj in obj.filter[key_operator]:
            node = f_obj.node
            root_node = node
            # root_node = f_obj.node

            field = f_obj.field
            if node is None:
                field_node = f_obj.field
            else:
                field_node = node
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

            # Apply comparison operator
            stmt = f_obj.operator.execute(left=stmt, right=values)
            exps.append(stmt)

            # Add filter to query object
        query = query.filter(FilterOperator(key_operator).execute(*exps))
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
                if element in _get_numeric_types():
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
        elif value_type in _get_numeric_types():
            statement = statement.cast(Numeric)
    return statement


def _get_numeric_types():
    return float, int, complex
