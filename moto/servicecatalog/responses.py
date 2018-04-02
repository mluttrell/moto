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
        idempotency_token = self._get_param('IdempotencyToken')
        portfolio = self.servicecatalog_backend.create_portfolio(display_name, provider_name, description, idempotency_token)
        return json.dumps({
            'PortfolioDetail': portfolio.response_object
        })

    def describe_portfolio(self):
        id = self._get_param('Id')
        portfolio = self.servicecatalog_backend.describe_portfolio(id)
        return json.dumps({
            'PortfolioDetail': portfolio.response_object
        })

    def list_portfolios(self):
        portfolios = self.servicecatalog_backend.list_portfolios()
        return json.dumps({
            'PortfolioDetails': [portfolio.response_object for portfolio in portfolios]
        })

    def create_product(self):
        name = self._get_param('Name')
        owner = self._get_param('Owner')
        distributor = self._get_param('Distributor')
        description = self._get_param('Description')
        support_description = self._get_param('SupportDescription')
        support_email = self._get_param('SupportEmail')
        support_url = self._get_param('SupportUrl')
        product_type = self._get_param('ProductType')
        idempotency_token = self._get_param('IdempotencyToken')
        provisioning_artifact = self._get_param('ProvisioningArtifactParameters')

        product = self.servicecatalog_backend.create_product(name, owner, distributor, description, support_description, support_email, support_url, product_type, provisioning_artifact, idempotency_token)
        return json.dumps(product.response_object)
