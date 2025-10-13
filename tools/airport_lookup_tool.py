"""
Airport Lookup Tool

This tool provides airport IATA codes and city names.
Can be used by AI agents to resolve city names to airport codes.
Fetches data from aviation-edge.com API or falls back to local cache.
"""

from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from utils.logger import setup_logger
import os
import json

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

    Fetches data from Amadeus API or uses cached fallback data.
    Caches results to minimize API calls.
    """

    # Cache for API results
    _airports_cache: Dict[str, AirportInfo] = {}
    _cache_timestamp: Optional[datetime] = None
    _cache_duration = timedelta(days=7)  # Cache airports for 7 days
    
    # Fallback airport database (loaded from file)
    FALLBACK_AIRPORTS: Dict[str, AirportInfo] = {}
    
    @classmethod
    def _load_fallback_airports(cls) -> Dict[str, AirportInfo]:
        """
        Load fallback airports from data file.
        
        Returns:
            Dictionary of IATA codes to AirportInfo objects
        """
        if cls.FALLBACK_AIRPORTS:
            return cls.FALLBACK_AIRPORTS
        
        airports = {}
        fallback_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "fallback_airports.txt"
        )
        
        try:
            with open(fallback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse airport line (format: IATA|CITY|COUNTRY|NAME|IS_MAJOR)
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            iata_code = parts[0].strip()
                            city = parts[1].strip()
                            country = parts[2].strip()
                            airport_name = parts[3].strip()
                            is_major = parts[4].strip().lower() == 'true'
                            
                            airports[iata_code] = AirportInfo(
                                iata_code=iata_code,
                                city=city,
                                country=country,
                                airport_name=airport_name,
                                is_major=is_major
                            )
            
            logger.debug(f"Loaded {len(airports)} fallback airports from file")
            cls.FALLBACK_AIRPORTS = airports
            return airports
            
        except FileNotFoundError:
            error_msg = f"Critical error: Fallback airports file not found at {fallback_file}. Please ensure the data/fallback_airports.txt file exists."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        except Exception as e:
            error_msg = f"Critical error loading fallback airports: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    @classmethod
    def _get_cache_file_path(cls) -> str:
        """Get the path to the airports cache file."""
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "airports_cache.json"
        )
    
    @classmethod
    def _load_cache_from_file(cls) -> bool:
        """
        Load airports cache from file.
        
        Returns:
            True if cache was loaded successfully
        """
        cache_file = cls._get_cache_file_path()
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Check if cache is still valid
                cache_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                if datetime.now() - cache_time < cls._cache_duration:
                    # Load airports from cache
                    for code, airport_data in data.get('airports', {}).items():
                        cls._airports_cache[code] = AirportInfo.model_validate(airport_data)
                    
                    cls._cache_timestamp = cache_time
                    logger.debug(f"Loaded {len(cls._airports_cache)} airports from cache")
                    return True
                else:
                    logger.debug("Airport cache expired")
                    return False
        except Exception as e:
            logger.warning(f"Failed to load airport cache: {e}")
            
        return False
    
    @classmethod
    def _save_cache_to_file(cls) -> None:
        """Save airports cache to file."""
        cache_file = cls._get_cache_file_path()
        
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            data = {
                'timestamp': cls._cache_timestamp.isoformat() if cls._cache_timestamp else datetime.now().isoformat(),
                'airports': {code: airport.model_dump() for code, airport in cls._airports_cache.items()}
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(cls._airports_cache)} airports to cache")
        except Exception as e:
            logger.warning(f"Failed to save airport cache: {e}")
    
    @classmethod
    def _fetch_airports_from_amadeus(cls) -> bool:
        """
        Fetch airports from Amadeus API.
        
        Returns:
            True if fetch was successful
        """
        try:
            from api.amadeus_client import AmadeusClient
            
            logger.info("Fetching airports from Amadeus API...")
            amadeus = AmadeusClient()
            
            # Note: Amadeus doesn't have a simple "get all airports" endpoint
            # So we'll use the fallback data as our primary source
            # In production, you could use a dedicated airports API
            
            logger.debug("Using fallback airports as Amadeus doesn't provide bulk airport data")
            return False
            
        except Exception as e:
            logger.warning(f"Failed to fetch from Amadeus: {e}")
            return False
    
    @classmethod
    def _ensure_airports_loaded(cls) -> None:
        """Ensure airports are loaded (from cache, API, or fallback)."""
        # If cache is already loaded and valid, return
        if cls._airports_cache and cls._cache_timestamp:
            time_since_cache = datetime.now() - cls._cache_timestamp
            if time_since_cache < cls._cache_duration:
                return
        
        # Try to load from file cache
        if cls._load_cache_from_file():
            return
        
        # Try to fetch from API (currently not implemented for Amadeus)
        # if cls._fetch_airports_from_amadeus():
        #     cls._cache_timestamp = datetime.now()
        #     cls._save_cache_to_file()
        #     return
        
        # Use fallback data from file
        logger.debug("Using fallback airport database from file")
        fallback_airports = cls._load_fallback_airports()
        cls._airports_cache = fallback_airports.copy()
        cls._cache_timestamp = datetime.now()
        cls._save_cache_to_file()

    @classmethod
    def get_airport_by_code(cls, iata_code: str) -> Optional[AirportInfo]:
        """
        Get airport information by IATA code.

        Args:
            iata_code: 3-letter IATA code (e.g., "JFK")

        Returns:
            AirportInfo object or None if not found
        """
        cls._ensure_airports_loaded()
        return cls._airports_cache.get(iata_code.upper())

    @classmethod
    def search_by_city(cls, city_name: str) -> List[AirportInfo]:
        """
        Search for airports by city name.

        Args:
            city_name: City name to search for

        Returns:
            List of matching airports
        """
        cls._ensure_airports_loaded()
        city_name_lower = city_name.lower()
        results = []

        for airport in cls._airports_cache.values():
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
        cls._ensure_airports_loaded()
        country_lower = country_name.lower()
        return [
            airport for airport in cls._airports_cache.values()
            if country_lower in airport.country.lower()
        ]

    @classmethod
    def get_all_airports(cls) -> List[AirportInfo]:
        """
        Get all airports in the database.

        Returns:
            List of all airports
        """
        cls._ensure_airports_loaded()
        return list(cls._airports_cache.values())

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
