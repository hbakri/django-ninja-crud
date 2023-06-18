import uuid

from django.db import models


class Identifiable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Representable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Collection(Identifiable, Representable):
    pass


class Item(Identifiable, Representable):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "collection"],
                name="unique_item_collection_name",
            ),
        ]
