from __future__ import unicode_literals

import json

from moto.core.responses import BaseResponse
from .models import servicecatalog_backends


class ServiceCatalogResponse(BaseResponse):
    @property
    def servicecatalog_backend(self):
        return servicecatalog_backends[self.region]

    def create_portfolio(self):
        display_name = self._get_param('DisplayName')
        description = self._get_param('Description')
        provider_name = self._get_param('ProviderName')
        idempotency_token = self._get_param('Idempotencytoken')
        portfolio = self.servicecatalog_backend.create_portfolio(display_name, provider_name, description, idempotency_token)
        return json.dumps({
            'PortfolioDetail': portfolio.response_object
        })