from __future__ import unicode_literals
from .responses import ServiceCatalogResponse

url_bases = [
    "https?://servicecatalog.(.+).amazonaws.com",
]

url_paths = {
    '{0}/$': ServiceCatalogResponse.dispatch,
}
