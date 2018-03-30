from __future__ import unicode_literals

import boto3
from botocore.exceptions import ClientError

import sure  # noqa
from moto import mock_servicecatalog


@mock_servicecatalog
def test_create_portfolio():
    conn = boto3.client('servicecatalog', region_name='us-east-1')
    response = conn.create_portfolio(
        DisplayName='Test Portfolio',
        Description='A test portfolio',
        ProviderName='Test provider',
        IdempotencyToken='123456'
    )

    response['PortfolioDetail']['Id'].should.equal('port-gmb6mfkd7tmjc')
    response['PortfolioDetail']['ARN'].should.equal('arn:aws:catalog:us-east-1:012345678910:portfolio/port-gmb6mfkd7tmjc')
    response['PortfolioDetail']['DisplayName'].should.equal('Test Portfolio')
    response['PortfolioDetail']['Description'].should.equal('A test portfolio')
    response['PortfolioDetail']['ProviderName'].should.equal('Test provider')