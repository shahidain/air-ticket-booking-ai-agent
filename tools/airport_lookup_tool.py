"""
Airport Lookup Tool

This tool provides airport IATA codes and city names.
Can be used by AI agents to resolve city names to airport codes.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AirportInfo(BaseModel):
    """Airport information model."""

    iata_code: str = Field(description="3-letter IATA airport code")
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    airport_name: str = Field(description="Full airport name")
    is_major: bool = Field(default=True, description="Whether this is a major international airport")


class AirportLookupTool:
    """
    Tool for looking up airport information.

    This tool maintains a database of major airports worldwide
    and can search by city name, airport code, or country.
    """

    # Comprehensive airport database
    AIRPORTS = {
        # United States
        "JFK": AirportInfo(iata_code="JFK", city="New York", country="USA",
                          airport_name="John F. Kennedy International Airport", is_major=True),
        "LGA": AirportInfo(iata_code="LGA", city="New York", country="USA",
                          airport_name="LaGuardia Airport", is_major=True),
        "EWR": AirportInfo(iata_code="EWR", city="New York", country="USA",
                          airport_name="Newark Liberty International Airport", is_major=True),
        "LAX": AirportInfo(iata_code="LAX", city="Los Angeles", country="USA",
                          airport_name="Los Angeles International Airport", is_major=True),
        "ORD": AirportInfo(iata_code="ORD", city="Chicago", country="USA",
                          airport_name="O'Hare International Airport", is_major=True),
        "MIA": AirportInfo(iata_code="MIA", city="Miami", country="USA",
                          airport_name="Miami International Airport", is_major=True),
        "SFO": AirportInfo(iata_code="SFO", city="San Francisco", country="USA",
                          airport_name="San Francisco International Airport", is_major=True),
        "SEA": AirportInfo(iata_code="SEA", city="Seattle", country="USA",
                          airport_name="Seattle-Tacoma International Airport", is_major=True),
        "LAS": AirportInfo(iata_code="LAS", city="Las Vegas", country="USA",
                          airport_name="Harry Reid International Airport", is_major=True),
        "BOS": AirportInfo(iata_code="BOS", city="Boston", country="USA",
                          airport_name="Logan International Airport", is_major=True),
        "IAD": AirportInfo(iata_code="IAD", city="Washington DC", country="USA",
                          airport_name="Washington Dulles International Airport", is_major=True),
        "DCA": AirportInfo(iata_code="DCA", city="Washington DC", country="USA",
                          airport_name="Ronald Reagan Washington National Airport", is_major=True),
        "ATL": AirportInfo(iata_code="ATL", city="Atlanta", country="USA",
                          airport_name="Hartsfield-Jackson Atlanta International Airport", is_major=True),
        "DFW": AirportInfo(iata_code="DFW", city="Dallas", country="USA",
                          airport_name="Dallas/Fort Worth International Airport", is_major=True),
        "DEN": AirportInfo(iata_code="DEN", city="Denver", country="USA",
                          airport_name="Denver International Airport", is_major=True),
        "PHX": AirportInfo(iata_code="PHX", city="Phoenix", country="USA",
                          airport_name="Phoenix Sky Harbor International Airport", is_major=True),

        # Europe
        "LHR": AirportInfo(iata_code="LHR", city="London", country="UK",
                          airport_name="Heathrow Airport", is_major=True),
        "LGW": AirportInfo(iata_code="LGW", city="London", country="UK",
                          airport_name="Gatwick Airport", is_major=True),
        "STN": AirportInfo(iata_code="STN", city="London", country="UK",
                          airport_name="Stansted Airport", is_major=True),
        "CDG": AirportInfo(iata_code="CDG", city="Paris", country="France",
                          airport_name="Charles de Gaulle Airport", is_major=True),
        "ORY": AirportInfo(iata_code="ORY", city="Paris", country="France",
                          airport_name="Orly Airport", is_major=True),
        "FRA": AirportInfo(iata_code="FRA", city="Frankfurt", country="Germany",
                          airport_name="Frankfurt Airport", is_major=True),
        "AMS": AirportInfo(iata_code="AMS", city="Amsterdam", country="Netherlands",
                          airport_name="Amsterdam Airport Schiphol", is_major=True),
        "MAD": AirportInfo(iata_code="MAD", city="Madrid", country="Spain",
                          airport_name="Adolfo Suárez Madrid-Barajas Airport", is_major=True),
        "BCN": AirportInfo(iata_code="BCN", city="Barcelona", country="Spain",
                          airport_name="Barcelona-El Prat Airport", is_major=True),
        "FCO": AirportInfo(iata_code="FCO", city="Rome", country="Italy",
                          airport_name="Leonardo da Vinci-Fiumicino Airport", is_major=True),
        "MXP": AirportInfo(iata_code="MXP", city="Milan", country="Italy",
                          airport_name="Milan Malpensa Airport", is_major=True),
        "IST": AirportInfo(iata_code="IST", city="Istanbul", country="Turkey",
                          airport_name="Istanbul Airport", is_major=True),
        "MUC": AirportInfo(iata_code="MUC", city="Munich", country="Germany",
                          airport_name="Munich Airport", is_major=True),
        "ZRH": AirportInfo(iata_code="ZRH", city="Zurich", country="Switzerland",
                          airport_name="Zurich Airport", is_major=True),

        # Middle East
        "DXB": AirportInfo(iata_code="DXB", city="Dubai", country="UAE",
                          airport_name="Dubai International Airport", is_major=True),
        "DOH": AirportInfo(iata_code="DOH", city="Doha", country="Qatar",
                          airport_name="Hamad International Airport", is_major=True),
        "AUH": AirportInfo(iata_code="AUH", city="Abu Dhabi", country="UAE",
                          airport_name="Abu Dhabi International Airport", is_major=True),

        # Asia
        "SIN": AirportInfo(iata_code="SIN", city="Singapore", country="Singapore",
                          airport_name="Singapore Changi Airport", is_major=True),
        "HKG": AirportInfo(iata_code="HKG", city="Hong Kong", country="Hong Kong",
                          airport_name="Hong Kong International Airport", is_major=True),
        "NRT": AirportInfo(iata_code="NRT", city="Tokyo", country="Japan",
                          airport_name="Narita International Airport", is_major=True),
        "HND": AirportInfo(iata_code="HND", city="Tokyo", country="Japan",
                          airport_name="Haneda Airport", is_major=True),
        "ICN": AirportInfo(iata_code="ICN", city="Seoul", country="South Korea",
                          airport_name="Incheon International Airport", is_major=True),
        "BKK": AirportInfo(iata_code="BKK", city="Bangkok", country="Thailand",
                          airport_name="Suvarnabhumi Airport", is_major=True),
        "KUL": AirportInfo(iata_code="KUL", city="Kuala Lumpur", country="Malaysia",
                          airport_name="Kuala Lumpur International Airport", is_major=True),
        "BOM": AirportInfo(iata_code="BOM", city="Mumbai", country="India",
                          airport_name="Chhatrapati Shivaji Maharaj International Airport", is_major=True),
        "DEL": AirportInfo(iata_code="DEL", city="Delhi", country="India",
                          airport_name="Indira Gandhi International Airport", is_major=True),
        "PEK": AirportInfo(iata_code="PEK", city="Beijing", country="China",
                          airport_name="Beijing Capital International Airport", is_major=True),
        "PVG": AirportInfo(iata_code="PVG", city="Shanghai", country="China",
                          airport_name="Shanghai Pudong International Airport", is_major=True),

        # Canada
        "YYZ": AirportInfo(iata_code="YYZ", city="Toronto", country="Canada",
                          airport_name="Toronto Pearson International Airport", is_major=True),
        "YVR": AirportInfo(iata_code="YVR", city="Vancouver", country="Canada",
                          airport_name="Vancouver International Airport", is_major=True),
        "YUL": AirportInfo(iata_code="YUL", city="Montreal", country="Canada",
                          airport_name="Montréal-Pierre Elliott Trudeau International Airport", is_major=True),

        # Oceania
        "SYD": AirportInfo(iata_code="SYD", city="Sydney", country="Australia",
                          airport_name="Sydney Kingsford Smith Airport", is_major=True),
        "MEL": AirportInfo(iata_code="MEL", city="Melbourne", country="Australia",
                          airport_name="Melbourne Airport", is_major=True),
        "AKL": AirportInfo(iata_code="AKL", city="Auckland", country="New Zealand",
                          airport_name="Auckland Airport", is_major=True),

        # Latin America
        "GRU": AirportInfo(iata_code="GRU", city="São Paulo", country="Brazil",
                          airport_name="São Paulo/Guarulhos International Airport", is_major=True),
        "MEX": AirportInfo(iata_code="MEX", city="Mexico City", country="Mexico",
                          airport_name="Mexico City International Airport", is_major=True),
        "EZE": AirportInfo(iata_code="EZE", city="Buenos Aires", country="Argentina",
                          airport_name="Ministro Pistarini International Airport", is_major=True),
    }

    @classmethod
    def get_airport_by_code(cls, iata_code: str) -> Optional[AirportInfo]:
        """
        Get airport information by IATA code.

        Args:
            iata_code: 3-letter IATA code (e.g., "JFK")

        Returns:
            AirportInfo object or None if not found
        """
        return cls.AIRPORTS.get(iata_code.upper())

    @classmethod
    def search_by_city(cls, city_name: str) -> List[AirportInfo]:
        """
        Search for airports by city name.

        Args:
            city_name: City name to search for

        Returns:
            List of matching airports
        """
        city_name_lower = city_name.lower()
        results = []

        for airport in cls.AIRPORTS.values():
            if city_name_lower in airport.city.lower():
                results.append(airport)

        return results

    @classmethod
    def get_primary_airport_for_city(cls, city_name: str) -> Optional[AirportInfo]:
        """
        Get the primary/major airport for a city.

        If multiple airports exist, returns the first major one.

        Args:
            city_name: City name

        Returns:
            Primary airport info or None
        """
        airports = cls.search_by_city(city_name)

        if not airports:
            return None

        # Return first major airport, or first airport if no major ones
        major_airports = [a for a in airports if a.is_major]
        return major_airports[0] if major_airports else airports[0]

    @classmethod
    def search_by_country(cls, country_name: str) -> List[AirportInfo]:
        """
        Get all airports in a country.

        Args:
            country_name: Country name

        Returns:
            List of airports in that country
        """
        country_lower = country_name.lower()
        return [
            airport for airport in cls.AIRPORTS.values()
            if country_lower in airport.country.lower()
        ]

    @classmethod
    def get_all_airports(cls) -> List[AirportInfo]:
        """
        Get all airports in the database.

        Returns:
            List of all airports
        """
        return list(cls.AIRPORTS.values())

    @classmethod
    def format_airports_list(cls, airports: List[AirportInfo]) -> str:
        """
        Format a list of airports for display.

        Args:
            airports: List of airport info objects

        Returns:
            Formatted string
        """
        if not airports:
            return "No airports found."

        result = []
        for airport in airports:
            result.append(
                f"- {airport.iata_code}: {airport.city}, {airport.country} "
                f"({airport.airport_name})"
            )

        return "\n".join(result)


# Tool function definitions for LLM to call
def lookup_airport_by_code(iata_code: str) -> str:
    """
    Look up airport information by IATA code.

    Args:
        iata_code: 3-letter IATA airport code (e.g., 'JFK', 'LAX')

    Returns:
        Airport information as formatted string
    """
    airport = AirportLookupTool.get_airport_by_code(iata_code)

    if airport:
        return (
            f"Airport: {airport.airport_name}\n"
            f"IATA Code: {airport.iata_code}\n"
            f"City: {airport.city}\n"
            f"Country: {airport.country}"
        )
    else:
        return f"Airport with code '{iata_code}' not found in database."


def lookup_airports_by_city(city_name: str) -> str:
    """
    Find all airports serving a city.

    Args:
        city_name: Name of the city (e.g., 'New York', 'London')

    Returns:
        List of airports serving that city
    """
    airports = AirportLookupTool.search_by_city(city_name)

    if airports:
        return AirportLookupTool.format_airports_list(airports)
    else:
        return f"No airports found for city '{city_name}'."


def get_primary_airport(city_name: str) -> str:
    """
    Get the primary airport IATA code for a city.

    This is useful for flight searches when you need a single airport code.

    Args:
        city_name: Name of the city

    Returns:
        IATA code of primary airport or error message
    """
    airport = AirportLookupTool.get_primary_airport_for_city(city_name)

    if airport:
        return airport.iata_code
    else:
        return f"No airport found for '{city_name}'."


# Export tool definitions for LangChain/OpenAI function calling
AIRPORT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_airport_by_code",
            "description": "Look up detailed airport information using its IATA code",
            "parameters": {
                "type": "object",
                "properties": {
                    "iata_code": {
                        "type": "string",
                        "description": "3-letter IATA airport code (e.g., 'JFK', 'LAX')"
                    }
                },
                "required": ["iata_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_airports_by_city",
            "description": "Find all airports serving a specific city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "Name of the city (e.g., 'New York', 'London')"
                    }
                },
                "required": ["city_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_primary_airport",
            "description": "Get the primary/main airport IATA code for a city. Use this when you need a single airport code for flight searches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "Name of the city"
                    }
                },
                "required": ["city_name"]
            }
        }
    }
]


# Map function names to actual functions
TOOL_FUNCTIONS = {
    "lookup_airport_by_code": lookup_airport_by_code,
    "lookup_airports_by_city": lookup_airports_by_city,
    "get_primary_airport": get_primary_airport
}
