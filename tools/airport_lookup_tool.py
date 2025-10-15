"""
Airport Lookup Tool

This tool provides airport IATA codes and city names.
Can be used by AI agents to resolve city names to airport codes.
Fetches real-time data from Amadeus Location API only.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from utils.logger import setup_logger

logger = setup_logger(__name__)


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

    Fetches data from Amadeus API in real-time.
    """

    @classmethod
    def _fetch_airport_from_amadeus(cls, city_or_code: str) -> List[AirportInfo]:
        """
        Fetch airport information from Amadeus API.

        Uses the Amadeus Location Search API to find airports by city name or IATA code.

        Args:
            city_or_code: City name or IATA code to search

        Returns:
            List of AirportInfo objects found
        """
        try:
            from api.amadeus_client import AmadeusClient

            logger.debug(f"Searching Amadeus API for airports: {city_or_code}")
            amadeus = AmadeusClient()

            # Use Amadeus Reference Data API - Locations endpoint
            response = amadeus.client.reference_data.locations.get(
                keyword=city_or_code,
                subType='AIRPORT'
            )

            airports = []

            if response.data:
                logger.debug(f"Found {len(response.data)} airports from Amadeus API")

                for location in response.data:
                    # Extract airport information
                    iata_code = location.get('iataCode', '')

                    if not iata_code:
                        continue

                    # Get address information
                    address = location.get('address', {})
                    city = address.get('cityName', '')
                    country = address.get('countryName', '')

                    # Airport name
                    airport_name = location.get('name', f"{city} Airport")

                    # Determine if major airport (Amadeus doesn't provide this directly)
                    # Consider it major if it's in a major city or has "International" in name
                    is_major = 'international' in airport_name.lower() or location.get('relevance', 0) > 5

                    airport_info = AirportInfo(
                        iata_code=iata_code,
                        city=city,
                        country=country,
                        airport_name=airport_name,
                        is_major=is_major
                    )

                    airports.append(airport_info)

                return airports
            else:
                logger.debug(f"No airports found in Amadeus API for: {city_or_code}")
                return []

        except Exception as e:
            logger.error(f"Failed to fetch from Amadeus API: {e}")
            raise

    @classmethod
    def get_airport_by_code(cls, iata_code: str) -> Optional[AirportInfo]:
        """
        Get airport information by IATA code using Amadeus API.

        Args:
            iata_code: 3-letter IATA code (e.g., "JFK")

        Returns:
            AirportInfo object or None if not found
        """
        logger.debug(f"Fetching airport '{iata_code}' from Amadeus API")
        amadeus_results = cls._fetch_airport_from_amadeus(iata_code)

        if amadeus_results:
            return amadeus_results[0]

        logger.warning(f"Airport '{iata_code}' not found in Amadeus API")
        return None

    @classmethod
    def search_by_city(cls, city_name: str) -> List[AirportInfo]:
        """
        Search for airports by city name using Amadeus API.

        Args:
            city_name: City name to search for

        Returns:
            List of matching airports
        """
        logger.info(f"Searching for airports in '{city_name}' via Amadeus API")
        amadeus_results = cls._fetch_airport_from_amadeus(city_name)
        
        if amadeus_results:
            logger.info(f"Found {len(amadeus_results)} airports from Amadeus API for '{city_name}'")
        else:
            logger.warning(f"No airports found for '{city_name}' in Amadeus API")

        return amadeus_results

    @classmethod
    def get_primary_airport_for_city(cls, city_name: str) -> Optional[AirportInfo]:
        """
        Get the primary/major airport for a city using Amadeus API.

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
    If multiple airports are found, prompts the user to select one.

    Args:
        city_name: Name of the city

    Returns:
        IATA code of primary airport or error message
    """
    airports = AirportLookupTool.search_by_city(city_name)
    
    if not airports:
        return f"No airport found for '{city_name}'."
    
    # If only one airport, return it directly
    if len(airports) == 1:
        return airports[0].iata_code
    
    # Multiple airports found - ask user to select
    print(f"\n🛫 Multiple airports found for '{city_name}':")
    print("=" * 70)
    for idx, airport in enumerate(airports, 1):
        major_tag = " ⭐ [MAJOR]" if airport.is_major else ""
        print(f"{idx}. {airport.iata_code} - {airport.airport_name}{major_tag}")
        print(f"   📍 {airport.city}, {airport.country}")
        print()
    
    while True:
        try:
            choice = input(f"Select airport (1-{len(airports)}) or 'cancel' to exit: ").strip()
            
            if choice.lower() in ['cancel', 'exit', 'quit']:
                raise KeyboardInterrupt("User cancelled airport selection")
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(airports):
                selected_airport = airports[choice_num - 1]
                print(f"✅ Selected: {selected_airport.iata_code} - {selected_airport.airport_name}\n")
                return selected_airport.iata_code
            else:
                print(f"❌ Invalid choice. Please enter a number between 1 and {len(airports)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            raise


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
