from datetime import date
from .sheets import load_active_properties

#dates = StatusDates(date.fromisoformat("2021-11-26"), date.fromisoformat("2022-01-06"), date.fromisoformat("2021-12-05"), None, date.fromisoformat("2022-01-06"))
#geo_data = GeolocationData(43.129518,-88.046977)
#address = Address("10850",Direction.W,"Appleton Ave", None,"Little Menomonee Parkway", "WI", "MIL", "53225",geo_data)
#additional_info = AdditionalInformation(None,None, None, False , False , False)
#attributes = PhysicalAttributes(1334, "Public record", "1924" , 4, 2, 1, 1, GarageType.N, 1.5, True, 32)
#test_property = Property(1773048, PropertyType.SINGLE_FAMILY, 189900,189900,195000, dates,address, additional_info, attributes, TermsOfSale.FHA);
#
#print(test_property)

load_active_properties()

