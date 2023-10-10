from dataclasses import dataclass
from enum import Enum
from datetime import date
from typing import Union

# TODO Import neighborhood data based on google maps longitude and latitude string
# The google sheets schema must be immutable and set, we cannot depend on the MLS export schema 

class Spreadsheet(Enum):
    SOLD = 'Sold!'
    ACTIVE = 'Active!'

class PropertyType(Enum):
    SINGLE_FAMILY = 1
    MULTI_FAMILY = 2
    DUPLEX = 3
    CONDO = 4
    APARTMENT = 5
    N_A = 6


def get_property_type_from_str(string : str):
    if string == "Single Family":
        return PropertyType.SINGLE_FAMILY

    return PropertyType.N_A


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
    direction : str 
    street_name : str
    neighborhood : str
    state : str
    county : str
    zip_code : str
    geo_data : Union[GeolocationData,None]

@dataclass(slots=True)
class PhysicalAttributes:
    square_footage : int
    build_year : str
    rooms : int
    bedrooms : int
    half_bathrooms : int
    full_bathrooms : int
    garage_space : float

@dataclass(slots=True)
class AdditionalInformation:
    private_remarks : Union[str, None]
    public_remarks : Union[str , None]
    showing_info  : Union[str, None]

@dataclass(slots=True)
class Property:
    list_number : int
    type : PropertyType
    agency_info : AgencyInfo
    original_list_price : int
    list_price : int
    sold_price : Union[int,None]
    status_dates : StatusDates
    address : Address
    additional_info : AdditionalInformation
    attribs : PhysicalAttributes

class PropertyFieldIndices:
    LIST_NUMBER = 0
    AGENCY_NAME = 1
    AGENCY_PHONE = 2
    LISTING_AGENT = 3
    PROPERTY_TYPE = 5
    LISTING_DATE = 13
    SOLD_DATE = 14
    PENDING_DATE = 15
    FALLTHROUGH = 16
    STATUS = 17
    STATUS_CHANGE_DATE = 18
    ORIGINAL_LIST_PRICE = 21
    LIST_PRICE = 22
    SOLD_PRICE = 23
    GARAGE_SPACES = 24
    TERMS_OF_SALE = 26
    STREET_NUM = 29
    STREET_DIR = 30
    STREET_NAME = 31
    STATE = 35
    COUNTY = 36
    ZIP_CODE = 37
    GEO_LAT = 38
    GEO_LONG = 39
    TOTAL_SQ_FT = 40
    BUILD_YEAR = 43
    N_OF_ROOMS = 47
    N_OF_BEDROOMS = 48
    N_FULL_BATHS = 50
    N_OF_HALF_BATHS = 51
    GARAGE_TYPE  = 52
    PRIVATE_REMARKS= 60
    PUBLIC_REMARKS = 59
    SHOWING_INFO = 62


def get_from_sheets_array(sheets_row):
    agency_info = AgencyInfo(sheets_row[PropertyFieldIndices.AGENCY_NAME],
    sheets_row[PropertyFieldIndices.AGENCY_PHONE],
    sheets_row[PropertyFieldIndices.LISTING_AGENT])

    status_dates = StatusDates(sheets_row[PropertyFieldIndices.LISTING_DATE],
    sheets_row[PropertyFieldIndices.SOLD_DATE],
    sheets_row[PropertyFieldIndices.PENDING_DATE],
    sheets_row[PropertyFieldIndices.FALLTHROUGH],
    sheets_row[PropertyFieldIndices.STATUS_CHANGE_DATE],)

    geo_data = GeolocationData(sheets_row[PropertyFieldIndices.GEO_LAT],
    sheets_row[PropertyFieldIndices.GEO_LONG])

    address_info = Address(sheets_row[PropertyFieldIndices.STREET_NUM],
    sheets_row[PropertyFieldIndices.STREET_DIR],
    sheets_row[PropertyFieldIndices.STREET_NAME], 
    "TODO ADD neighborhood=",
    sheets_row[PropertyFieldIndices.STATE],
    sheets_row[PropertyFieldIndices.COUNTY],
    sheets_row[PropertyFieldIndices.ZIP_CODE],
    geo_data
    )

    attribs = PhysicalAttributes(sheets_row[PropertyFieldIndices.TOTAL_SQ_FT],
    sheets_row[PropertyFieldIndices.BUILD_YEAR],
    sheets_row[PropertyFieldIndices.N_OF_ROOMS],
    sheets_row[PropertyFieldIndices.N_OF_BEDROOMS],
    sheets_row[PropertyFieldIndices.N_OF_HALF_BATHS],
    sheets_row[PropertyFieldIndices.N_FULL_BATHS],
    sheets_row[PropertyFieldIndices.GARAGE_SPACES])

    additional_info = AdditionalInformation(
            sheets_row[PropertyFieldIndices.PRIVATE_REMARKS],
            sheets_row[PropertyFieldIndices.PUBLIC_REMARKS],
            sheets_row[PropertyFieldIndices.SHOWING_INFO],
        )

    return Property(
    sheets_row[PropertyFieldIndices.LIST_NUMBER],
    sheets_row[PropertyFieldIndices.PROPERTY_TYPE],
    agency_info,
    sheets_row[PropertyFieldIndices.ORIGINAL_LIST_PRICE],
    sheets_row[PropertyFieldIndices.LIST_PRICE],
    sheets_row[PropertyFieldIndices.SOLD_PRICE],
    status_dates,
    address_info,
    additional_info,
    attribs)

