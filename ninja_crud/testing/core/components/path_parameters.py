from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class PathParameters:
    """
    Manages HTTP path parameters for various test scenarios.

    The PathParameters class is designed to simplify the process of defining and using different sets of
    path parameters for multiple test scenarios. It supports defining path parameters for successful
    requests (`ok`), as well as path parameters expected to result in not found (`not_found`) responses.

    One of the key features is its ability to accept either a single dictionary (for testing a single
    case) or a list of dictionaries (for testing multiple cases), providing a convenient way to test
    various scenarios with minimal setup.

    Example:
    ```python
    from ninja_crud.testing.core.components import PathParameters

    # Single case
    single_path_parameters = PathParameters(ok={"id": 1})

    # Multiple cases
    multiple_path_parameters = PathParameters(
        ok=[{"id": 1}, {"id": 2}],
        not_found=[{"id": 3}]
    )
    ```
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        not_found: Union[dict, List[dict], None] = None,
    ) -> None:
        """
        Initializes the PathParameters instance, allowing for the specification of various
        path parameter configurations.

        Args:
            ok (Union[dict, List[dict]]): Path parameters for successful resolution. Can be a single
                dictionary representing one test case or a list of dictionaries for multiple test cases.
            not_found (Union[dict, List[dict], None], optional): Path parameters expected to lead to a
                'not found' outcome. Accepts either a single dictionary or a list of dictionaries. Defaults to None.
        """
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.not_found: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(not_found) if not_found is not None else None
        )
