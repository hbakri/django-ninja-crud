from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class QueryParameters:
    """
    This class is used to manage query parameters used in HTTP requests.

    This class allows you to define sets of query parameters for different test scenarios. Specifically,
    it enables you to set up parameters that should result in successful requests ('ok') and parameters
    that should result in 'bad request' responses.

    Example:
        >>> from ninja_crud.testing.core.components import QueryParameters
        >>> query_parameters = QueryParameters(
        ...     ok=[{"search": "item"}, {"page": 2, "limit": 10}],
        ...     bad_request=[{"page": -1}, {"limit": "invalid"}],
        ... )
        >>> query_parameters.ok
        [{'search': 'item'}, {'page': 2, 'limit': 10}]
        >>> query_parameters.bad_request
        [{'page': -1}, {'limit': 'invalid'}]
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        bad_request: Union[dict, List[dict], None] = None,
    ) -> None:
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.bad_request: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(bad_request) if bad_request is not None else None
        )
