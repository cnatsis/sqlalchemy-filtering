from sqlalchemy import nullslast

from sqlalchemy_filter_json.validators import SortRequest, SortDirection


def sort_apply(query, entity, obj: SortRequest = None):
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
    # if "sort" not in obj.keys():
    #     return query
    if obj.sort is None:
        return query

    sort_obj = obj.sort
    if len(sort_obj) != 0:
        for sort_request in sort_obj:
            node_sort = sort_request.node
            sort_split = node_sort.split('.')
            if len(sort_split) == 0:
                sort_stmt = getattr(entity, sort_request.json_field)[sort_request.node]
            else:
                sort_stmt = getattr(entity, sort_request.json_field)
                for s in sort_split:
                    sort_stmt = sort_stmt[s]

            direction = sort_request.direction
            nulls_last = sort_request.nullsLast

            if direction is None or direction == SortDirection.ASC:
                sort_stmt = sort_stmt.asc()
            elif direction == SortDirection.DESC:
                sort_stmt = sort_stmt.desc()
            else:
                # TODO redundant - delete it?
                raise Exception('Invalid `{}` order by direction'.format(direction))

            if nulls_last is not None and nulls_last:
                sort_stmt = nullslast(sort_stmt)

            # Apply order by to query
            query = query.order_by(sort_stmt)
        return query
