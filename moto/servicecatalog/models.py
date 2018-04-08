
from moto.core import BaseBackend, BaseModel
import boto3
import random
import string
import uuid
from datetime import datetime
from .exceptions import PortfolioNotFoundException

default_account_id = '012345678910'


def generate_service_catalog_id(prefix):
    return '{0}-{1}'.format(prefix, ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(13)))


def filter_optional_values(dictionary):
    return {key: value for key, value in dictionary.items() if value is not None}


class Portfolio(BaseModel):

    def __init__(self, name, provider_name, description=None):
        self.name = name
        self.provider_name = provider_name
        self.description = description

        self.id = generate_service_catalog_id('port')
        self.arn = 'arn:aws:catalog:us-east-1:{0}:portfolio/{1}'.format(default_account_id, self.id)
        self.created_time = datetime.now()
        self.products = []

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

    def add_product(self, product):
        self.products.append(product)


class Product(BaseModel):

    def __init__(self, name, owner, distributor, description, support_description, support_email, support_url, product_type, provisioning_artifact):
        self.id = generate_service_catalog_id('prodview')
        self.product_id = generate_service_catalog_id('prod')
        self.arn = 'arn:aws:catalog:us-east-1:{0}:product/{1}'.format(default_account_id, self.product_id)
        self.provisioning_artifact = ProvisioningArtifact(provisioning_artifact)
        self.name = name
        self.owner = owner
        self.distributor = distributor
        self.description = description
        self.support_description = support_description
        self.support_email = support_email
        self.support_url = support_url
        self.type = product_type

        self.created_time = datetime.now()
        self.portfolios = []

    def associate_with_portfolio(self, portfolio):
        self.portfolios.append(portfolio)

    @property
    def has_default_path(self):
        return bool(self.portfolios)

    @property
    def product_view_detail(self):
        product_view_summary = {
            'Id': self.id,
            'ProductId': self.product_id,
            'Name': self.name,
            'Owner': self.owner,
            'ShortDescription': self.description,
            'Type': self.type,
            'Distributor': self.distributor,
            'HasDefaultPath': self.has_default_path,
            'SupportEmail': self.support_email,
            'SupportDescription': self.support_description,
            'SupportUrl': self.support_url
        }
        product_view_summary = filter_optional_values(product_view_summary)

        product_view_detail = {
            'ProductViewSummary': product_view_summary,
            'Status': 'AVAILABLE',
            'ProductARN': self.arn,
            'CreatedTime': str(self.created_time)
        }

        return product_view_detail

    @property
    def response_object(self):
        response_object = {}

        response_object['ProductViewDetail'] = self.product_view_detail
        response_object['ProvisioningArtifactDetail'] = self.provisioning_artifact.response_object

        return response_object

    @property
    def response_summary(self):
        response_object = {}

        response_object['ProductViewDetail'] = self.product_view_detail
        response_object['ProvisioningArtifactSummaries'] = [
            self.provisioning_artifact.response_summary
        ]

        return response_object


class ProvisioningArtifact(BaseModel):

    def __init__(self, provisioning_artifact):
        self.id = generate_service_catalog_id('pa')
        self.name = provisioning_artifact.get('Name', None)
        self.description = provisioning_artifact.get('Description', None)
        self.info = provisioning_artifact['Info']
        self.type = provisioning_artifact.get('Type', '')
        self.created_time = datetime.now()

    @property
    def response_object(self):
        response_object = {}
        response_object['Id'] = self.id
        response_object['Type'] = self.type
        response_object['CreatedTime'] = str(self.created_time)
        response_object['Active'] = True
        response_object['Name'] = self.name
        response_object['Description'] = self.description
        response_object = filter_optional_values(response_object)

        return response_object

    @property
    def response_summary(self):
        response_object = {}
        response_object['Id'] = self.id
        response_object['Name'] = self.name
        response_object['Description'] = self.description
        response_object['CreatedTime'] = str(self.created_time)
        return response_object


class ServiceCatalogBackend(BaseBackend):

    def __init__(self):
        self.portfolios = {}
        self.products = {}

        self.portfolio_idempotency = {}
        self.product_idempotency = {}

    def create_portfolio(self, name, provider_name, description, idempotency_token):
        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())

        if idempotency_token not in self.portfolio_idempotency:
            portfolio = Portfolio(name, provider_name, description)
            self.portfolio_idempotency[idempotency_token] = portfolio.id
            self.portfolios[portfolio.id] = portfolio
        else:
            portfolio_id = self.portfolio_idempotency[idempotency_token]
            portfolio = self.portfolios[portfolio_id]

        return portfolio

    def describe_portfolio(self, id):
        if id not in self.portfolios:
            raise PortfolioNotFoundException(id)

        return self.portfolios[id]

    def list_portfolios(self):
        return list(self.portfolios.values())

    def create_product(self, name, owner, distributor, description, support_description, support_email, support_url, product_type, provisioning_artifact, idempotency_token):
        if idempotency_token is None:
            idempotency_token = str(uuid.uuid4())

        if idempotency_token not in self.product_idempotency:
            product = Product(name, owner, distributor, description, support_description, support_email, support_url, product_type, provisioning_artifact)
            self.product_idempotency[idempotency_token] = product.product_id
            self.products[product.product_id] = product
        else:
            product_id = self.product_idempotency[idempotency_token]
            product = self.products[product_id]

        return product

    def associate_product_with_portfolio(self, portfolio_id, product_id):
        portfolio = self.portfolios[portfolio_id]
        product = self.products[product_id]

        portfolio.add_product(product)
        product.associate_with_portfolio(portfolio)

    def describe_product_as_admin(self, product_id):
        # TODO: what to do if product does not exist?
        return self.products[product_id]


available_regions = boto3.session.Session().get_available_regions("servicecatalog")
servicecatalog_backends = {region: ServiceCatalogBackend() for region in available_regions}
