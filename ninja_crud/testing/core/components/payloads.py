from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class Payloads:
    """
    Manages HTTP request payloads for various test scenarios.

    The Payloads class is designed to simplify the process of defining and using different sets of
    payloads for multiple test scenarios. It supports defining payloads for successful requests ('ok'),
    as well as payloads expected to result in bad request ('bad_request') or conflict ('conflict')
    responses.

    One of the key features is its ability to accept either a single dictionary (for testing a single
    case) or a list of dictionaries (for testing multiple cases), providing a convenient way to test
    various scenarios with minimal setup.

    Example:
    ```python
    from ninja_crud.testing.core.components import Payloads

    # Single case
    single_payloads = Payloads(ok={"name": "ok"})

    # Multiple cases
    multiple_payloads = Payloads(
        ok=[{"name": "ok1"}, {"name": "ok2"}],
        bad_request=[{"name": "bad_request"}],
        conflict=[{"name": "conflict"}]
    )
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        bad_request: Union[dict, List[dict], None] = None,
        conflict: Union[dict, List[dict], None] = None,
    ) -> None:
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.bad_request: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(bad_request) if bad_request is not None else None
        )
        self.conflict: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(conflict) if conflict is not None else None
        )
