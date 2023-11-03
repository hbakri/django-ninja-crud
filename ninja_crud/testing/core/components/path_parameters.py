from typing import List, Optional, Union

from ninja_crud.testing.core.components import utils


class PathParameters:
    """
    This class is used to manage path parameters used in HTTP requests.

    This class allows you to define sets of path parameters for different test scenarios. Specifically,
    it enables you to set up parameters that should result in successful requests ('ok') and parameters
    that should result in 'not found' responses.

    Example:
        >>> from ninja_crud.testing.core.components import PathParameters
        >>> path_parameters = PathParameters(
        ...     ok=[{"id": 1}, {"id": 2}],
        ...     not_found=[{"id": 3}, {"id": 4}],
        ... )
        >>> path_parameters.ok
        [{'id': 1}, {'id': 2}]
        >>> path_parameters.not_found
        [{'id': 3}, {'id': 4}]
    """

    def __init__(
        self,
        ok: Union[dict, List[dict]],
        not_found: Union[dict, List[dict], None] = None,
    ) -> None:
        self.ok: List[dict] = utils.ensure_list_of_dicts(ok)
        self.not_found: Optional[List[dict]] = (
            utils.ensure_list_of_dicts(not_found) if not_found is not None else None
        )
