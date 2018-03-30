from __future__ import unicode_literals
from .models import servicecatalog_backends
from ..core.models import base_decorator, deprecated_base_decorator

servicecatalog_backend = servicecatalog_backends['us-east-1']
mock_servicecatalog = base_decorator(servicecatalog_backends)
mock_servicecatalog_deprecated = deprecated_base_decorator(servicecatalog_backends)
