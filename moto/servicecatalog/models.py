
from moto.core import BaseBackend, BaseModel
import boto3

default_account_id = '012345678910'

class Portfolio(BaseModel):

    def __init__(self, name, provider_name, description=None, idempotency_token=None):
        self.name = name
        self.provider_name = provider_name
        self.description = description
        self.idempotency_token = idempotency_token
        self.id = 'port-gmb6mfkd7tmjc'
        self.arn = 'arn:aws:catalog:us-east-1:{0}:portfolio/{1}'.format(default_account_id, self.id)

    @property
    def response_object(self):
        response_object = {}
        response_object['Id'] = self.id
        response_object['ARN'] = self.arn
        response_object['DisplayName'] = self.name
        response_object['Description'] = self.description
        #response_object['CreatedTime'] = self.uri
        response_object['ProviderName'] = self.provider_name
        return response_object

class ServiceCatalogBackend(BaseBackend):

    def __init__(self):
        self.portfolios = {}

    def create_portfolio(self, name, provider_name, description, idempotency_token):
        portfolio = Portfolio(name, provider_name, description, idempotency_token)
        self.portfolios[name] = portfolio
        return portfolio

available_regions = boto3.session.Session().get_available_regions("servicecatalog")
servicecatalog_backends = {region: ServiceCatalogBackend() for region in available_regions}