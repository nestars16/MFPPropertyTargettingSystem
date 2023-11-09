from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import Union
from math import sqrt
from datetime import datetime

DATE_FORMATS = [ "%Y-%m-%d","%m/%d/%Y" ]
DEFAULT_DATE_FORMAT = "%m/%d/%Y" 


ACTIVE_SHEET_ID = '1l_vdszegyTa7FCPqL8WcZ-iV_FzQWFFyE6uggZYV22A'
SOLD_SHEET_ID = '1S8HXWayHcro3O_xMCjaFuMiVWjAgdjyhObqCVtKXJaQ'
DASHBOARD_SHEET_ID = '1GxSKElRyVSRlh8rQzthN9KPPNhQM3IGDCXWsya4X6Fw'
MASTER_SOLDS_SHEET_ID = '1c-TvmHyjhzTCDT4nj78avuk1pDPbgmyM86ZfpRZlH9U'
# GOOGLE_API_KEY = 'AIzaSyC22y_wJabYLGr1ZX44LF22xLqaCy1ZfOU'
# gmaps = googlemaps.Client(key=GOOGLE_API_KEY)





# TODO Import neighborhood data based on google maps longitude and latitude string
# The google sheets schema must be immutable and set, we cannot depend on the MLS export schema 

@dataclass(slots=True)
class SheetInfo:
    Id : str
    name : str
    info_sheet : str
    range : str

class Spreadsheet(Enum):
    SOLD = SheetInfo(SOLD_SHEET_ID, "'Import Solds'!","Formatted!", "A2:AN")
    ACTIVE = SheetInfo(ACTIVE_SHEET_ID, "'Import Actives'!","Formatted!","A2:AH" )
    OUTPUT = SheetInfo(DASHBOARD_SHEET_ID, "Result!","N/A", "N/A")
    MASTER_SOLDS = SheetInfo(MASTER_SOLDS_SHEET_ID, "'Master Solds'!", "'Master Solds'!", "A2:AN")

class PropertyCategory(Enum):
    ACTIVE = 1
    SOLD = 2

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

    # def get_neighborhood(self):

    #     try:
    #         # pylint: disable=maybe-no-member
    #         reverse_geocode_result = gmaps.reverse_geocode((self.latitude, self.longitude))
    #     except ValueError:
    #         return ""

    #     neighborhood = None

    #     for result in reverse_geocode_result:
    #         for component in result['address_components']:
    #             if 'neighborhood' in component['types']:
    #                 neighborhood = component['long_name']

    #     return neighborhood if neighborhood else ""

    def get_distance_from_sold(self, sold):
        try :
            longitude = float(self.longitude)
            latitude = float(self.latitude)
            lat_diff = 69 * (latitude - float(sold.address.geo_data.latitude))
            lon_diff = 50 * (longitude - float(sold.address.geo_data.longitude))
            distance = sqrt(lat_diff**2 + lon_diff**2)
            return distance
        except ValueError:
            return 0



@dataclass(slots=True)
class Address:
    street_number : str
    direction : str
    street_name : str
    neighborhood : str
    state : str
    county : str
    zip_code : str
    geo_data : GeolocationData

@dataclass(slots=True)
class PhysicalAttributes:
    square_footage : int
    build_year : str
    rooms : int
    bedrooms : int
    half_bathrooms : int
    full_bathrooms : int
    garage_space : float

    def get_bathroom_float(self):
        try:
            return int(self.full_bathrooms) + int(self.half_bathrooms)/2
        except ValueError:
            return 0

@dataclass(slots=True)
class AdditionalInformation:
    private_remarks : str
    public_remarks : str
    showing_info  : str


def default_agency_info():
    return AgencyInfo("", "")

def default_status_dates():
    return StatusDates(date(1900, 1, 1), None, None, None, None)

def default_geolocation_data():
    return GeolocationData(0.0, 0.0)

def default_address():
    return Address("", "", "", "", "", "", "", default_geolocation_data())

def default_additional_information():
    return AdditionalInformation("", "", "")

def default_physical_attributes():
    return PhysicalAttributes(0, "1900", 0, 0, 0, 0, 0.0)


@dataclass(slots=True)
class Property:
    list_number : str = ""
    agency_info : AgencyInfo = field(default_factory=default_agency_info)
    original_list_price : int = 0
    list_price : int = 0
    sold_price : int = 0
    status_dates : StatusDates = field(default_factory=default_status_dates)
    address : Address = field(default_factory=default_address)
    additional_info : AdditionalInformation = field(default_factory=default_additional_information)
    attribs : PhysicalAttributes = field(default_factory=default_physical_attributes)

    def get_price_psft(self):
        try:
            return int(self.sold_price)/ int(self.attribs.square_footage)
        except ValueError:
            return -1
        except ZeroDivisionError:
            return -1


class PropertyFieldIndices():
    LIST_NUMBER = 0
    AGENCY_NAME = 1
    AGENCY_PHONE = 2
    LISTING_AGENT = 3
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
    NEIGHBORHOOD = 33

class FormattedSoldFieldIndices():
    LIST_NUMBER = 0
    AGENCY_PHONE = 1
    LISTING_AGENT = 2
    LISTING_DATE = 3
    SOLD_DATE = 4
    PENDING_DATE = 5
    STATUS_CHANGE_DATE = 6
    ORIGINAL_LIST_PRICE = 7
    LIST_PRICE = 8
    SOLD_PRICE = 9
    GARAGE_SPACES = 10
    TERMS_OF_SALE = 11
    STREET_NUM = 12
    STREET_DIR = 13
    STREET_NAME = 14
    MUNICIPALITY = 16
    STATE = 17
    COUNTY = 18
    ZIP_CODE = 19
    GEO_LAT = 20
    GEO_LONG = 21
    TOTAL_SQ_FT = 22
    BUILD_YEAR = 23
    N_OF_ROOMS = 24
    N_OF_BEDROOMS = 25
    N_OF_FULL_BATHS = 27
    N_OF_HALF_BATHS = 28
    NEIGHBORHOOD = 39

class FormattedActiveFieldIndices():
    LIST_NUMBER = 0
    LISTING_AGENT = 1
    AGENCY_PHONE = 2
    LISTING_DATE = 3
    STATUS_CHANGE_DATE = 4
    ORIGINAL_LIST_PRICE = 5
    LIST_PRICE = 6
    STREET_NUM = 7
    STREET_DIR = 8
    STREET_NAME = 9
    MUNICIPALITY = 11
    STATE = 12
    COUNTY = 13
    ZIP_CODE = 14
    GEO_LAT = 15
    GEO_LONG = 16
    TOTAL_SQ_FT = 17
    BUILD_YEAR = 18
    N_OF_ROOMS = 19
    N_OF_BEDROOMS = 20
    N_OF_FULL_BATHS = 22
    N_OF_HALF_BATHS = 23
    NEIGHBORHOOD = 33

def get_date(date_str):
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(date_str,date_format)
        except ValueError:
            continue

    return datetime.strptime("1/1/1970", DEFAULT_DATE_FORMAT)


def get_float(float_str):
    try:
        return float(float_str)
    except ValueError:
        return 0.0

def get_int(int_str):
    try:
        return int(int_str)
    except ValueError:
        return 0


def get_sold_from_sheets(sheets_row):

    agency_info = AgencyInfo(
            sheets_row[FormattedSoldFieldIndices.AGENCY_PHONE],
            sheets_row[FormattedSoldFieldIndices.LISTING_AGENT]
    )

    listing_date = get_date(sheets_row[FormattedSoldFieldIndices.LISTING_DATE])
    sold_date = get_date(sheets_row[FormattedSoldFieldIndices.SOLD_DATE])
    pending_date = get_date(sheets_row[FormattedSoldFieldIndices.PENDING_DATE])


    status_change_date = get_date(sheets_row[FormattedSoldFieldIndices.STATUS_CHANGE_DATE])

    status_dates = StatusDates(listing_date,sold_date,pending_date,None,status_change_date)
    
    geo_data = GeolocationData(
            get_float(sheets_row[FormattedSoldFieldIndices.GEO_LAT]), 
            get_float(sheets_row[FormattedSoldFieldIndices.GEO_LONG])
    )


    address_info = Address(sheets_row[FormattedSoldFieldIndices.STREET_NUM],
    sheets_row[FormattedSoldFieldIndices.STREET_DIR],
    sheets_row[FormattedSoldFieldIndices.STREET_NAME],
    sheets_row[FormattedSoldFieldIndices.NEIGHBORHOOD],
    sheets_row[FormattedSoldFieldIndices.STATE],
    sheets_row[FormattedSoldFieldIndices.COUNTY],
    sheets_row[FormattedSoldFieldIndices.ZIP_CODE],
    geo_data
    )


    total_sq_ft = get_int(sheets_row[FormattedSoldFieldIndices.TOTAL_SQ_FT])
    n_of_rooms = get_int(sheets_row[FormattedSoldFieldIndices.N_OF_ROOMS])
    n_of_bedrooms = get_int(sheets_row[FormattedSoldFieldIndices.N_OF_BEDROOMS])
    n_of_half_baths = get_int(sheets_row[FormattedSoldFieldIndices.N_OF_HALF_BATHS])
    n_of_full_baths = get_int(sheets_row[FormattedSoldFieldIndices.N_OF_FULL_BATHS])
    garage_spaces = get_float(sheets_row[FormattedSoldFieldIndices.GARAGE_SPACES])


    attribs = PhysicalAttributes(
    total_sq_ft,
    sheets_row[FormattedSoldFieldIndices.BUILD_YEAR],
    n_of_rooms,
    n_of_bedrooms,
    n_of_half_baths,
    n_of_full_baths,
    garage_spaces
    )

    additional_info = default_additional_information()


    orginal_list_price = get_int(sheets_row[FormattedSoldFieldIndices.ORIGINAL_LIST_PRICE])
    list_price = get_int(sheets_row[FormattedSoldFieldIndices.LIST_PRICE])
    sold_price = get_int(sheets_row[FormattedSoldFieldIndices.SOLD_PRICE])


    return Property(
    sheets_row[FormattedSoldFieldIndices.LIST_NUMBER],
    agency_info,
    orginal_list_price,
    list_price,
    sold_price,
    status_dates,
    address_info,
    additional_info,
    attribs
    )



def get_active_from_sheets(sheets_row):

    agency_info = AgencyInfo(
            sheets_row[FormattedActiveFieldIndices.AGENCY_PHONE],
            sheets_row[FormattedActiveFieldIndices.LISTING_AGENT]
    )

    listing_date = get_date(sheets_row[FormattedActiveFieldIndices.LISTING_DATE]);

    sold_date = datetime.strptime("1/1/1970",DEFAULT_DATE_FORMAT)
    pending_date = datetime.strptime("1/1/1970",DEFAULT_DATE_FORMAT)

    status_change_date = get_date(sheets_row[FormattedActiveFieldIndices.STATUS_CHANGE_DATE]);

    status_dates = StatusDates(listing_date,sold_date,pending_date,None,status_change_date)
    
    geo_data = GeolocationData(
            get_float(sheets_row[FormattedActiveFieldIndices.GEO_LAT]), 
            get_float(sheets_row[FormattedActiveFieldIndices.GEO_LONG])
    )


    address_info = Address(sheets_row[FormattedActiveFieldIndices.STREET_NUM],
    sheets_row[FormattedActiveFieldIndices.STREET_DIR],
    sheets_row[FormattedActiveFieldIndices.STREET_NAME],
    sheets_row[FormattedActiveFieldIndices.NEIGHBORHOOD],
    sheets_row[FormattedActiveFieldIndices.STATE],
    sheets_row[FormattedActiveFieldIndices.COUNTY],
    sheets_row[FormattedActiveFieldIndices.ZIP_CODE],
    geo_data
    )


    total_sq_ft = get_int(sheets_row[FormattedActiveFieldIndices.TOTAL_SQ_FT])
    n_of_rooms = get_int(sheets_row[FormattedActiveFieldIndices.N_OF_ROOMS])
    n_of_bedrooms = get_int(sheets_row[FormattedActiveFieldIndices.N_OF_BEDROOMS])
    n_of_half_baths = get_int(sheets_row[FormattedActiveFieldIndices.N_OF_HALF_BATHS])
    n_of_full_baths = get_int(sheets_row[FormattedActiveFieldIndices.N_OF_FULL_BATHS])
    garage_spaces = 0.0


    attribs = PhysicalAttributes(
    total_sq_ft,
    sheets_row[FormattedActiveFieldIndices.BUILD_YEAR],
    n_of_rooms,
    n_of_bedrooms,
    n_of_half_baths,
    n_of_full_baths,
    garage_spaces
    )

    additional_info = default_additional_information()


    orginal_list_price = get_int(sheets_row[FormattedActiveFieldIndices.ORIGINAL_LIST_PRICE])
    list_price = get_int(sheets_row[FormattedActiveFieldIndices.LIST_PRICE])

    sold_price = 0


    return Property(
    sheets_row[FormattedActiveFieldIndices.LIST_NUMBER],
    agency_info,
    orginal_list_price,
    list_price,
    sold_price,
    status_dates,
    address_info,
    additional_info,
    attribs
    )




@dataclass(slots=True)
class PropertyResult:
    score : float
    property: Property

    def __lt__(self, other):
        return self.score < other.score

@dataclass(slots=True)
class BestComps:
    active : Property
    best_comps : list[PropertyResult]
    third_quartile_price : float

    def get_arv_avg(self):
        total = 0
        prop_number = 0
        for comp in self.best_comps:
            try:
                total += int(comp.property.sold_price)
                prop_number += 1
            except ValueError:
                print(f"Property {comp.property.list_number} has no sold price")

        return total / prop_number


    def get_result_array(self):

        comp_arv = self.get_arv_avg()
        try:
            sf_arv = int(self.active.attribs.square_footage) * self.third_quartile_price
        except ValueError:
            sf_arv = 0

        arv_avg = (0.75 * comp_arv) + (0.25 * sf_arv)

        try:
            percentage_avg_arv = int(self.active.list_price)/arv_avg
        except ValueError:
            percentage_avg_arv = 0
        except ZeroDivisionError:
            percentage_avg_arv = 0


        try:
            list_p_sqft = int(self.active.list_price) / int(self.active.attribs.square_footage)
        except ValueError:
            list_p_sqft = 0
        except ZeroDivisionError:
            list_p_sqft = 0


        result_row = [
        self.active.list_number,
        self.active.address.geo_data.latitude,
        self.active.address.geo_data.longitude,
        self.active.list_price,
        arv_avg,
        comp_arv,
        sf_arv,
        percentage_avg_arv,
        self.active.address.neighborhood,
        self.active.attribs.bedrooms,
        self.active.attribs.get_bathroom_float(),
        self.active.attribs.square_footage,
        list_p_sqft,
        self.third_quartile_price,
        ]

        for comp in reversed(self.best_comps):
            result_row.extend([float(comp.property.sold_price),comp.property.list_number])

        return result_row



def get_from_sheets_array(sheets_row):
    agency_info = AgencyInfo(
    sheets_row[PropertyFieldIndices.AGENCY_PHONE],
    sheets_row[PropertyFieldIndices.LISTING_AGENT])

    status_dates = StatusDates(sheets_row[PropertyFieldIndices.LISTING_DATE],
    sheets_row[PropertyFieldIndices.SOLD_DATE],
    sheets_row[PropertyFieldIndices.PENDING_DATE],
    sheets_row[PropertyFieldIndices.FALLTHROUGH],
    sheets_row[PropertyFieldIndices.STATUS_CHANGE_DATE],)

    try:
        geo_data = GeolocationData(float(sheets_row[PropertyFieldIndices.GEO_LAT]),
        float(sheets_row[PropertyFieldIndices.GEO_LONG]))
    except ValueError:
        geo_data = GeolocationData(0.0,0.0)

    address_info = Address(sheets_row[PropertyFieldIndices.STREET_NUM],
    sheets_row[PropertyFieldIndices.STREET_DIR],
    sheets_row[PropertyFieldIndices.STREET_NAME],
    sheets_row[PropertyFieldIndices.NEIGHBORHOOD],#geo_data.get_neighborhood(),
    sheets_row[PropertyFieldIndices.STATE],
    sheets_row[PropertyFieldIndices.COUNTY],
    sheets_row[PropertyFieldIndices.ZIP_CODE],
    geo_data
    )


    try:
        total_sq_ft = int(sheets_row[PropertyFieldIndices.TOTAL_SQ_FT])
    except ValueError:
        total_sq_ft = 0

    try:
        n_of_rooms = int(sheets_row[PropertyFieldIndices.N_OF_ROOMS])
    except ValueError:
        n_of_rooms = 0

    try:
        n_of_bedrooms = int(sheets_row[PropertyFieldIndices.N_OF_BEDROOMS])
    except ValueError:
        n_of_bedrooms = 0

    try:
        n_of_half_baths = int(sheets_row[PropertyFieldIndices.N_OF_HALF_BATHS])
    except ValueError:
        n_of_half_baths = 0

    try:
        n_of_full_baths = int(sheets_row[PropertyFieldIndices.N_FULL_BATHS])
    except ValueError:
        n_of_full_baths = 0

    try:
        garage_spaces = float(sheets_row[PropertyFieldIndices.GARAGE_SPACES])
    except ValueError:
        garage_spaces = 0


    attribs = PhysicalAttributes(
    total_sq_ft,
    sheets_row[PropertyFieldIndices.BUILD_YEAR],
    n_of_rooms,
    n_of_bedrooms,
    n_of_half_baths,
    n_of_full_baths,
    garage_spaces
    )
    

    additional_info = AdditionalInformation(
            sheets_row[PropertyFieldIndices.PRIVATE_REMARKS],
            sheets_row[PropertyFieldIndices.PUBLIC_REMARKS],
            sheets_row[PropertyFieldIndices.SHOWING_INFO],
        )

    return Property(
    sheets_row[PropertyFieldIndices.LIST_NUMBER],
    agency_info,
    sheets_row[PropertyFieldIndices.ORIGINAL_LIST_PRICE],
    sheets_row[PropertyFieldIndices.LIST_PRICE],
    sheets_row[PropertyFieldIndices.SOLD_PRICE],
    status_dates,
    address_info,
    additional_info,
    attribs)
