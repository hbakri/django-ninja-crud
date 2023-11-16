from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class QueryParameters:
    """
    Manages HTTP query parameters for various test scenarios.

    The QueryParameters class is designed to simplify the process of defining and using different sets of
    query parameters for multiple test scenarios. It supports defining query parameters for successful
    requests (`ok`), as well as query parameters expected to result in bad request (`bad_request`)
    responses.

    One of the key features is its ability to accept either a single dictionary (for testing a single
    case) or a list of dictionaries (for testing multiple cases), providing a convenient way to test
    various scenarios with minimal setup.

    Example:
    ```python
    from ninja_crud.testing.core.components import QueryParameters

    # Single case
    single_query_parameters = QueryParameters(ok={"page": 2, "limit": 10})

    # Multiple cases
    multiple_query_parameters = QueryParameters(
        ok=[{"page": 1, "limit": 10}, {"page": 2, "limit": 10}],
        bad_request=[{"page": 1, "limit": 0}]
    )
    ```
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        bad_request: Union[dict, List[dict], None] = None,
    ) -> None:
        """
        Initializes the QueryParameters instance, allowing for the specification of various
        query parameter configurations.

        Args:
            ok (Union[dict, List[dict]]): Query parameters for successful resolution. Can be a single
                dictionary representing one test case or a list of dictionaries for multiple test cases.
            bad_request (Union[dict, List[dict], None], optional): Query parameters expected to lead to a
                'bad request' outcome. Accepts either a single dictionary or a list of dictionaries.
                Defaults to None.
        """
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.bad_request: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(bad_request) if bad_request is not None else None
        )
