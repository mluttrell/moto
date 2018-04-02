
from moto.core import BaseBackend, BaseModel
import boto3
import random
import string
import uuid
from datetime import datetime
from .exceptions import PortfolioNotFoundException

default_account_id = '012345678910'


class Portfolio(BaseModel):

    def __init__(self, name, provider_name, description=None, idempotency_token=None):
        self.name = name
        self.provider_name = provider_name
        self.description = description

        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())

        self.idempotency_token = idempotency_token

        self.id = 'port-{0}'.format(''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(13)))
        self.arn = 'arn:aws:catalog:us-east-1:{0}:portfolio/{1}'.format(default_account_id, self.id)
        self.created_time = datetime.now()

    @property
    def response_object(self):
        response_object = {}
        response_object['Id'] = self.id
        response_object['ARN'] = self.arn
        response_object['DisplayName'] = self.name
        response_object['Description'] = self.description
        response_object['ProviderName'] = self.provider_name
        response_object['CreatedTime'] = str(self.created_time)
        return response_object


class ServiceCatalogBackend(BaseBackend):

    def __init__(self):
        self.portfolios = {}
        self.idempotency = {}

    def create_portfolio(self, name, provider_name, description, idempotency_token):
        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())

        if idempotency_token not in self.idempotency:
            portfolio = Portfolio(name, provider_name, description, idempotency_token)
            self.idempotency[idempotency_token] = portfolio.id
            self.portfolios[portfolio.id] = portfolio
        else:
            portfolio_id = self.idempotency[idempotency_token]
            portfolio = self.portfolios[portfolio_id]

        return portfolio

    def describe_portfolio(self, id):
        if id not in self.portfolios:
            raise PortfolioNotFoundException(id)

        return self.portfolios[id]

    def list_portfolios(self):
        return list(self.portfolios.values())


available_regions = boto3.session.Session().get_available_regions("servicecatalog")
servicecatalog_backends = {region: ServiceCatalogBackend() for region in available_regions}
