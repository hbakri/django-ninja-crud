from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class Headers:
    """
    Manages HTTP request headers for various test scenarios.

    The Headers class is designed to simplify the process of defining and using different sets of
    headers for multiple test scenarios. It supports defining headers for successful requests (`ok`),
    as well as headers expected to result in forbidden (`forbidden`) or unauthorized (`unauthorized`)
    responses.

    One of the key features is its ability to accept either a single dictionary (for testing a single
    case) or a list of dictionaries (for testing multiple cases), providing a convenient way to test
    various scenarios with minimal setup.

    Example:
    ```python
    from ninja_crud.testing.core.components import Headers

    # Single case
    single_headers = Headers(ok={"HTTP_AUTHORIZATION": "Bearer ok"})

    # Multiple cases
    multiple_headers = Headers(
        ok=[{"HTTP_AUTHORIZATION": "Bearer ok1"}, {"HTTP_AUTHORIZATION": "Bearer ok2"}],
        forbidden=[{"HTTP_AUTHORIZATION": "Bearer forbidden"}],
        unauthorized=[{}]
    )
    ```
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        forbidden: Union[dict, List[dict], None] = None,
        unauthorized: Union[dict, List[dict], None] = None,
    ) -> None:
        """
        Initializes the Headers instance, allowing for the specification of various header configurations.

        Args:
            ok (Union[dict, List[dict]]): Headers for successful requests. Can be a single dictionary
                for one test case, or a list of dictionaries for multiple cases.
            forbidden (Union[dict, List[dict], None], optional): Headers expected to yield a 'forbidden'
                response. Accepts a single dictionary or a list of dictionaries. Defaults to None.
            unauthorized (Union[dict, List[dict], None], optional): Headers expected to yield an 'unauthorized'
                response. Like `ok` and `forbidden`, it accepts both a single dictionary or a list. Defaults to None.
        """
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.forbidden: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(forbidden) if forbidden is not None else None
        )
        self.unauthorized: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(unauthorized)
            if unauthorized is not None
            else None
        )
