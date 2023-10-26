from dataclasses import dataclass, field
from enum import Enum
from datetime import date
from typing import Union
import googlemaps # pylint: disable=import-error
from math import sqrt


GOOGLE_API_KEY = 'AIzaSyC22y_wJabYLGr1ZX44LF22xLqaCy1ZfOU'
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

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

    def get_neighborhood(self):

        try:
            # pylint: disable=maybe-no-member
            reverse_geocode_result = gmaps.reverse_geocode((self.latitude, self.longitude))
        except ValueError:
            return ""

        neighborhood = None

        for result in reverse_geocode_result:
            for component in result['address_components']:
                if 'neighborhood' in component['types']:
                    neighborhood = component['long_name']

        return neighborhood if neighborhood else ""

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
    return AgencyInfo("", "", "")

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


def get_from_sheets_array(sheets_row):
    agency_info = AgencyInfo(sheets_row[PropertyFieldIndices.AGENCY_NAME],
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
        self.third_quartile_price,
        ]

        for comp in self.best_comps:
            result_row.extend([comp.property.sold_price,comp.property.list_number])

        return result_row
