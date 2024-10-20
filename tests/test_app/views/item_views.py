from functools import wraps

from django.core.exceptions import PermissionDenied
from ninja import Router

from ninja_crud import views
from ninja_crud.viewsets import APIViewSet
from tests.test_app.models import Item, Tag
from tests.test_app.schemas import ItemIn, ItemOut, OrderByFilter, TagOut

router = Router()


def user_is_collection_creator(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        item_id = getattr(kwargs.get("path_parameters"), "id", None)
        item = Item.objects.get(id=item_id)
        if item.collection.created_by != request.auth:
            raise PermissionDenied()
        return func(request, *args, **kwargs)

    return wrapper


class ItemViewSet(APIViewSet):
    model = Item
    default_request_body = ItemIn
    default_response_body = ItemOut

    list_items = views.ListView(
        query_parameters=OrderByFilter,
        get_queryset=lambda request, path_parameters: Item.objects.get_queryset(),
    )
    read_item = views.ReadView(
        get_model=lambda request, path_parameters: Item.objects.get(
            id=path_parameters.id
        ),
        decorators=[user_is_collection_creator],
    )
    update_item = views.UpdateView(
        pre_save=lambda request, instance: None,
        post_save=lambda request, instance: None,
        decorators=[user_is_collection_creator],
    )
    delete_item = views.DeleteView(decorators=[user_is_collection_creator])

    list_tags = views.ListView(
        path="/{id}/tags/",
        get_queryset=lambda request, path_parameters: Tag.objects.filter(
            items__id=path_parameters.id
        ),
        response_body=list[TagOut],
    )


ItemViewSet.add_views_to(router)
