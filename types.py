from dataclasses import dataclass
from enum import Enum
from datetime import date
from typing import Union

# TODO Import neighborhood data based on google maps longitude and latitude string
# The google sheets schema must be immutable and set, we cannot depend on the MLS export schema 

class PropertyType(Enum):
    SINGLE_FAMILY = 1
    MULTI_FAMILY = 2
    DUPLEX = 3
    CONDO = 4
    APARTMENT = 5

class PropertyStatus(Enum):
    ACTIVE = 1
    ACTIVE_CONTIGENT = 2
    PENDING = 3
    EXPIRED = 4
    SOLD = 5
    CANCELLED = 6
    WITHDRAWN = 7

class Direction(Enum):
    N = 1
    S = 2
    W = 3
    E = 4

class GarageType(Enum):
    D = 1
    N = 2
    A = 3

class Zoning(Enum):
    SINGLE = 1
    RST2 = 2
    RST3 = 4
    RST4 = 5
    RST5 = 6
    RST6 = 7
    RESIDENTIAL = 8
    LB2 = 9

class TermsOfSale(Enum):
    CONV = 1
    FHA = 2
    CASH = 3
    ARM = 4
    WHEDA = 5
    VA = 6
    OTHER = 7

@dataclass(slots=True)
class AgencyInfo:
    agency_name : str
    agency_phone : str
    listing_agent : str
    co_listing_agent : Union[str,None]

@dataclass(slots=True)
class StatusDates:
    listing : date
    sold : Union[date, None]
    pending : Union[date, None]
    fallthrough : Union[date, None]
    status_change_date : Union[date, None]

@dataclass(slots=True)
class GeolocationData:
    latitude : float
    longitude : float

@dataclass(slots=True)
class Address:
    street_number : str 
    direction : Direction
    street_name : str
    unit_number : Union[str,None]
    neighborhood : str
    state : str
    county : str
    zip_code : str
    geo_data : Union[GeolocationData,None]

@dataclass(slots=True)
class PhysicalAttributes:
    square_footage : int
    sq_ft_src : str
    build_year : str
    rooms : int
    bedrooms : int
    half_bathrooms : int
    full_bathrooms : int
    garage : GarageType
    garage_space : float
    electronic_consent : bool
    days_on_market : int

@dataclass(slots=True)
class AdditionalInformation:
    private_remarks : Union[list[str], None]
    public_remarks : Union[list[str] , None]
    showing_info  : Union[list[str], None]
    broker_owned : Union[bool, None]
    named_prospects : Union[bool, None]
    exclusive_agency : Union[bool, None]

@dataclass(slots=True)
class Property:
    list_number : int
    type : PropertyType
    original_list_price : int
    list_price : int
    sold_price : Union[int,None]
    status_dates : StatusDates
    address : Address
    additional_info : AdditionalInformation
    attribs : PhysicalAttributes
    term_of_sale : Union[TermsOfSale, None]
