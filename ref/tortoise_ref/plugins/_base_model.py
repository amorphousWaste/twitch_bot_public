"""Base plugin model."""

from tortoise import fields
from tortoise.models import Model


class AbstractPluginModel(Model):
    """Abstract table model for all plugins."""

    id = fields.IntField(pk=True)
    last_user_id = fields.ForeignKeyField('models.Users')
    last_run = fields.CharField(max_length=255, default='1970-01-01 00:00:00')

    class Meta:
        abstract = True
