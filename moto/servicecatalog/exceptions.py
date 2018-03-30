from __future__ import unicode_literals
from moto.core.exceptions import RESTError


class PortfolioNotFoundException(RESTError):
    code = 400

    def __init__(self, portfolio_name):
        super(PortfolioNotFoundException, self).__init__(
            error_type="PortfolioNotFoundException",
            message="Portfolio {0} not found.".format(portfolio_name))