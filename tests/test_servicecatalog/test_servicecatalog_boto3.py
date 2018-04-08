from __future__ import unicode_literals

import boto3

import sure  # noqa
from moto import mock_servicecatalog
from botocore.exceptions import ClientError


@mock_servicecatalog
def test_create_portfolio():
    conn = boto3.client('servicecatalog', region_name='us-east-1')
    response = conn.create_portfolio(
        DisplayName='Test Portfolio',
        Description='A test portfolio',
        ProviderName='Test provider'
    )

    response['PortfolioDetail']['Id'].should.match(r'port-[a-z0-9]{13}$')
    response['PortfolioDetail']['ARN'].should.equal('arn:aws:catalog:us-east-1:012345678910:portfolio/{0}'.format(response['PortfolioDetail']['Id']))
    response['PortfolioDetail']['DisplayName'].should.equal('Test Portfolio')
    response['PortfolioDetail']['Description'].should.equal('A test portfolio')
    response['PortfolioDetail']['ProviderName'].should.equal('Test provider')

@mock_servicecatalog
def test_create_portfolio_with_same_idempotency_token():
    conn = boto3.client('servicecatalog', region_name='us-east-1')
    idempotency_token = 'mytesttoken123'
    response1 = conn.create_portfolio(
        DisplayName='Test Portfolio',
        Description='A test portfolio',
        ProviderName='Test provider',
        IdempotencyToken=idempotency_token
    )

    response2 = conn.create_portfolio(
        DisplayName='Test Portfolio',
        Description='A test portfolio',
        ProviderName='Test provider',
        IdempotencyToken=idempotency_token
    )

    response2['PortfolioDetail']['Id'].should.equal(response1['PortfolioDetail']['Id'])

@mock_servicecatalog
def test_create_portfolio_with_different_idempotency_token():
    conn = boto3.client('servicecatalog', region_name='us-east-1')
    response1 = conn.create_portfolio(
        DisplayName='Test Portfolio',
        Description='A test portfolio',
        ProviderName='Test provider',
        IdempotencyToken='token1'
    )

    response2 = conn.create_portfolio(
        DisplayName='Test Portfolio',
        Description='A test portfolio',
        ProviderName='Test provider',
        IdempotencyToken='token2'
    )

    response2['PortfolioDetail']['Id'].should_not.equal(response1['PortfolioDetail']['Id'])

@mock_servicecatalog
def test_describe_portfolio():
    conn = boto3.client('servicecatalog', region_name='us-east-1')
    create_response = conn.create_portfolio(DisplayName='Test Portfolio', ProviderName='Test provider', Description='A test portfolio')

    response = conn.describe_portfolio(Id=create_response['PortfolioDetail']['Id'])

    response['PortfolioDetail']['Id'].should.match(r'port-[a-z0-9]{13}$')
    response['PortfolioDetail']['ARN'].should.equal('arn:aws:catalog:us-east-1:012345678910:portfolio/{0}'.format(response['PortfolioDetail']['Id']))
    response['PortfolioDetail']['DisplayName'].should.equal('Test Portfolio')
    response['PortfolioDetail']['Description'].should.equal('A test portfolio')
    response['PortfolioDetail']['ProviderName'].should.equal('Test provider')

@mock_servicecatalog
def test_describe_portfolio_that_doesnt_exist():
    conn = boto3.client('servicecatalog', region_name='us-east-1') 

    conn.describe_portfolio.when.called_with(
        Id='port-doesnotexist'
    ).should.throw(ClientError, 'Portfolio {0} not found.'.format('port-doesnotexist'))

@mock_servicecatalog
def test_list_portfolios():
    conn = boto3.client('servicecatalog', region_name='us-east-1')

    conn.create_portfolio(DisplayName='Test Portfolio 1', ProviderName='Test provider')
    conn.create_portfolio(DisplayName='Test Portfolio 2', ProviderName='Test provider')

    response = conn.list_portfolios()

    type(response['PortfolioDetails']).should.be(list)
    len(response['PortfolioDetails']).should.be(2)

    response['PortfolioDetails'][0]['DisplayName'] = 'Test Portfolio 1'
    response['PortfolioDetails'][1]['DisplayName'] = 'Test Portfolio 2'

@mock_servicecatalog
def test_create_product():
    conn = boto3.client('servicecatalog', region_name='us-east-1')

    response = conn.create_product(
        Name='Test product',
        Owner='Test owner',
        Description='Test description',
        Distributor='Test distributor',
        SupportDescription='Test support description',
        SupportEmail='test_support_email@someaddress.com',
        SupportUrl='http://test_support_url.com',
        ProductType='CLOUD_FORMATION_TEMPLATE',
        ProvisioningArtifactParameters={
            'Name': 'Test product version 1',
            'Description': 'Version 1 description',
            'Info': {
                'LoadTemplateFromUrl': 'https://s3.amazonaws.com/some_test_bucket/test.json'
            },
            'Type': 'CLOUD_FORMATION_TEMPLATE'
        }
    )

    product_view_summary = response['ProductViewDetail']['ProductViewSummary']
    product_view_summary['Id'].should.match(r'prodview-[a-z0-9]{13}$')
    product_view_summary['ProductId'].should.match(r'prod-[a-z0-9]{13}$')
    product_view_summary['Name'].should.equal('Test product')
    product_view_summary['Owner'].should.equal('Test owner')
    product_view_summary['ShortDescription'].should.equal('Test description')
    product_view_summary['Type'].should.equal('CLOUD_FORMATION_TEMPLATE')
    product_view_summary['Distributor'].should.equal('Test distributor')
    product_view_summary['HasDefaultPath'].should.equal(False)
    product_view_summary['SupportEmail'].should.equal('test_support_email@someaddress.com')
    product_view_summary['SupportDescription'].should.equal('Test support description')
    product_view_summary['SupportUrl'].should.equal('http://test_support_url.com')

    response['ProductViewDetail']['Status'].should.equal('CREATED')
    response['ProductViewDetail']['ProductARN'].should.equal('arn:aws:catalog:us-east-1:012345678910:product/{0}'.format(product_view_summary['ProductId']))

    provisioning_artifact_detail = response['ProvisioningArtifactDetail']
    provisioning_artifact_detail['Id'].should.match(r'pa-[a-z0-9]{13}$')
    provisioning_artifact_detail['Name'].should.equal('Test product version 1')
    provisioning_artifact_detail['Description'].should.equal('Version 1 description')
    provisioning_artifact_detail['Type'].should.equal('CLOUD_FORMATION_TEMPLATE')
    provisioning_artifact_detail['Active'].should.equal(True)

@mock_servicecatalog
def test_associate_product_with_portfolio():
    conn = boto3.client('servicecatalog', region_name='us-east-1')

    portfolio_response = conn.create_portfolio(DisplayName='Test Portfolio 1', ProviderName='Test provider')

    product_response = conn.create_product(
        Name='Test product',
        Owner='Test owner',
        ProductType='CLOUD_FORMATION_TEMPLATE',
        ProvisioningArtifactParameters={
            'Name': 'Test product version 1',
            'Info': {
                'LoadTemplateFromUrl': 'https://s3.amazonaws.com/some_test_bucket/test.json'
            }
        }
    )

    response = conn.associate_product_with_portfolio(
        ProductId=product_response['ProductViewDetail']['ProductViewSummary']['ProductId'],
        PortfolioId=portfolio_response['PortfolioDetail']['Id']
    )

    print(response)
    len(response.keys()).should.equal(1)
    response['ResponseMetadata'].should_not.be.empty

@mock_servicecatalog
def test_product_has_default_path():
    pass