import json
from sqlalchemy import Numeric
from sqlalchemy.sql.elements import BinaryExpression

from sqlalchemy_filtering.operators import FilterOperator, SQLDialect
from sqlalchemy_filtering.validators import FilterRequest, Filter, _get_numeric_types, SQLAlchemyField


def filter_apply(query, entity, obj: FilterRequest = None, dialect: SQLDialect = None):
    """
    Construct filters on SQLAlchemy query

    :param query: Query object of type :class:`sqlalchemy.orm.Query`.
    :param entity: SQLAlchemy model class.
    :param obj: :class:`FilterRequest` object.
    :param dialect: :class:`SQLDialect` enum object

        Example object

        -- Simple request
        obj = {
            "filter": [
                {
                    "field": "demographics",
                    "node": "age",
                    "operator": ">=",
                    "value": 20
                },
                {
                     "field": "demographics",
                     "node": "first_name",
                     "operator": "like",
                     "value": "%Test%"
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
                        "value": 20
                    },
                    {
                         "field": "demographics",
                         "node": "first_name",
                         "operator": "like",
                         "value": "%Test%"
                    }
                ]
            ],
            "sort": [...]
        }

        -- JSON request
        obj =
            "filter": [
                {
                    "field": "details",
                    "node": "user_details",
                    "operator": "@>",
                    "valueType": "jsonb",
                    "value": "[{\"skill\":\"Fighting\",\"rating\":10}]"
                }
            ],
            "sort": [...]
        }

    :returns: Query object of type :class:`sqlalchemy.orm.Query` with applied filters.
    """
    exps = []
    if obj.filter is None:
        return query

    for key_operator in obj.filter.keys():
        for f_obj in obj.filter[key_operator]:
            node = f_obj.node
            root_node = f_obj.field

            field = f_obj.field
            field_node = f_obj.field if node is None else node
            values = f_obj.value

            if type(values) is Filter:
                new_values: Filter = values
                tmp_new_node = new_values.node
                new_values.node = node + '.' + new_values.field
                if tmp_new_node is not None:
                    new_values.node = new_values.node + '.' + tmp_new_node
                new_values.field = root_node
                new_values.operator = new_values.operator.operator
                query_obj = {"filter": [new_values.__dict__]}
                query = filter_apply(query, entity, FilterRequest(query_obj), dialect=dialect)
                continue

            # Get model field
            node_split = field_node.split('.')
            if len(node_split) == 1 and type(values) is not dict:
                if field == field_node:
                    stmt = SQLAlchemyField(entity, field).get_field()
                else:
                    stmt = SQLAlchemyField(entity, field).get_field()[field_node]
            else:
                stmt = SQLAlchemyField(entity, field).get_field()
                for n in field_node.split('.'):
                    stmt = stmt[n]

            # Cast fields
            stmt = _cast_statement(stmt, f_obj, dialect)

            # Apply comparison operator
            stmt = f_obj.operator.execute(left=stmt, right=values)
            exps.append(stmt)

        # Add filter to query object
        query = query.filter(FilterOperator(key_operator).execute(*exps))
    return query


def _cast_statement(statement, obj: Filter = None, dialect: SQLDialect = None):
    """
    Cast statements to match database field types.

    :param statement:
        SQLAlchemy expression of types
        `sqlalchemy.sql.elements.BinaryExpression` (used on simple queries)
        or `sqlalchemy.orm.attributes.InstrumentedAttribute` (used on advanced JSON queries).
    :param obj: :class:`Filter` object.
    :param dialect: :class:`SQLDialect` enum object
    :return: :class:`sqlalchemy.sql.elements.BinaryExpression` or `sqlalchemy.orm.attributes.InstrumentedAttribute`.
    """
    values = obj.value

    if isinstance(statement, BinaryExpression) and dialect == SQLDialect.POSTGRESQL:
        value_type = type(values)
        if value_type is list:
            if len(values) != 0:
                element = type(values[0])
                statement = statement.cast(Numeric) if element in _get_numeric_types() else statement.astext
            else:
                return statement
        elif value_type is str:
            try:
                json.loads(values)
                return statement
            except ValueError:
                statement = statement.astext
        elif value_type in _get_numeric_types():
            statement = statement.cast(Numeric)
    return statement
