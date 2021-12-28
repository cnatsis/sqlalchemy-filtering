from sqlalchemy import nullslast

from sqlalchemy_filtering.validators import SortRequest, SortDirection, SQLAlchemyField


def sort_apply(query, entity, obj: SortRequest = None):
    """
    Construct sorting statements on SQLAlchemy query
    :param query: Query object of type :class:`sqlalchemy.orm.Query`.
    :param entity: SQLAlchemy model class.
    :param obj: :class:`SortRequest` object.

        Example object

        -- Simple request
        obj = {
            "filter": [...],
            "sort": [
                {
                    "field": "demographics",
                    "node": "age",
                    "direction": "asc",
                    "nullsLast": True
                }
            ]
        }

        -- Nested request
        obj = {
            "filter": [...],
            "sort": [
                {
                    "field": "demographics",
                    "node": "nested.field1",
                    "direction": "asc",
                    "nullsLast": True
                }
            ]
        }

    :return: Query object of type :class:`sqlalchemy.orm.Query` with applied sorting statements.
    """
    if obj.sort is None:
        return query

    sort_obj = obj.sort
    if len(sort_obj) != 0:
        for sort_request in sort_obj:
            node_sort = sort_request.field if sort_request.node is None else sort_request.node

            sort_split = node_sort.split('.')
            if len(sort_split) == 0:
                sort_stmt = SQLAlchemyField(entity, sort_request.field).get_field()[sort_request.node]
            else:
                sort_stmt = SQLAlchemyField(entity, sort_request.field).get_field()
                for s in sort_split:
                    if s is not node_sort:
                        sort_stmt = sort_stmt[s]

            direction = sort_request.direction
            nulls_last = sort_request.nullsLast

            sort_stmt = sort_stmt.asc() if (direction is None or direction == SortDirection.ASC) else sort_stmt.desc()

            if nulls_last is not None and nulls_last:
                sort_stmt = nullslast(sort_stmt)

            # Apply order by clause to query
            query = query.order_by(sort_stmt)
        return query
