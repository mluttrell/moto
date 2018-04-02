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
        DisplayName='Test Portfolio 2',
        Description='A test portfolio 2',
        ProviderName='Test provider 2',
        IdempotencyToken=idempotency_token
    )

    response2['PortfolioDetail']['Id'].should.equal(response1['PortfolioDetail']['Id'])
    response2['PortfolioDetail']['ARN'].should.equal(response1['PortfolioDetail']['ARN'])
    response2['PortfolioDetail']['DisplayName'].should.equal(response1['PortfolioDetail']['DisplayName'])
    response2['PortfolioDetail']['Description'].should.equal(response1['PortfolioDetail']['Description'])
    response2['PortfolioDetail']['ProviderName'].should.equal(response1['PortfolioDetail']['ProviderName'])
    response2['PortfolioDetail']['CreatedTime'].should.equal(response1['PortfolioDetail']['CreatedTime'])

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
        DisplayName='Test Portfolio 2',
        Description='A test portfolio 2',
        ProviderName='Test provider 2',
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
