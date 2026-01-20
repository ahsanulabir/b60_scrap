"""
Scrapers Package
Individual news source scrapers
"""

from .prothomalo import scrape_prothomalo
from .dailystar import scrape_dailystar
from .tbs import scrape_tbs
from .bdpratidin import scrape_bdpratidin
from .bbc import scrape_bbc
from .jagonews24 import scrape_jagonews24
from .bangla_tribune import scrape_bangla_tribune
from .bd24live import scrape_bd24live

# All available scrapers
SCRAPERS = {
    'prothomalo': scrape_prothomalo,
    'dailystar': scrape_dailystar,
    'tbs': scrape_tbs,
    'bdpratidin': scrape_bdpratidin,
    'bbc': scrape_bbc,
    'jagonews24': scrape_jagonews24,
    'bangla_tribune': scrape_bangla_tribune,
    'bd24live': scrape_bd24live,
}

__all__ = [
    'SCRAPERS',
    'scrape_prothomalo',
    'scrape_dailystar',
    'scrape_tbs',
    'scrape_bdpratidin',
    'scrape_bbc',
    'scrape_jagonews24',
    'scrape_bangla_tribune',
    'scrape_bd24live',
]
