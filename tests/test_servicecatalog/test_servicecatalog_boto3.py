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