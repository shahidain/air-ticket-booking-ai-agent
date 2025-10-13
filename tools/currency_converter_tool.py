"""
Currency Converter Tool

This tool provides currency conversion functionality for flight prices.
Can be used as a standalone function or by AI agents for currency conversion.
"""

import requests
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class CurrencyConverterTool:
    """
    Currency converter tool with caching to minimize API calls.
    
    Uses exchangerate-api.com for free exchange rates.
    """
    
    # Cache for exchange rates
    _rates_cache: Dict[str, float] = {}
    _cache_timestamp: Optional[datetime] = None
    _cache_duration = timedelta(hours=1)  # Cache rates for 1 hour
    
    # Fallback exchange rates (loaded from file)
    FALLBACK_RATES: Dict[str, float] = {}
    
    @classmethod
    def _load_fallback_rates(cls) -> Dict[str, float]:
        """
        Load fallback exchange rates from data file.
        
        Returns:
            Dictionary of currency codes to rates
        """
        if cls.FALLBACK_RATES:
            return cls.FALLBACK_RATES
        
        rates = {}
        fallback_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "fallback_exchange_rates.txt"
        )
        
        try:
            with open(fallback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse rate line (format: CURRENCY_CODE=RATE)
                    if '=' in line:
                        code, rate = line.split('=', 1)
                        rates[code.strip()] = float(rate.strip())
            
            logger.debug(f"Loaded {len(rates)} fallback exchange rates from file")
            cls.FALLBACK_RATES = rates
            return rates
            
        except FileNotFoundError:
            logger.error(f"Fallback rates file not found: {fallback_file}")
            # Return minimal fallback
            return {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.12}
        except Exception as e:
            logger.error(f"Error loading fallback rates: {e}")
            return {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.12}
    
    @classmethod
    def _should_refresh_cache(cls) -> bool:
        """Check if cache should be refreshed."""
        if cls._cache_timestamp is None:
            return True
        
        time_since_cache = datetime.now() - cls._cache_timestamp
        return time_since_cache > cls._cache_duration
    
    @classmethod
    def _fetch_exchange_rates(cls, base_currency: str = "USD") -> None:
        """
        Fetch current exchange rates from API.
        
        Args:
            base_currency: Base currency for rates (default: USD)
        """
        try:
            # Get API URL from config
            api_base_url = settings.exchange_rate_api_url
            url = f"{api_base_url}/{base_currency}"
            
            logger.debug(f"Fetching exchange rates from {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result") == "success":
                    cls._rates_cache = data.get("rates", {})
                    cls._cache_timestamp = datetime.now()
                    logger.info(
                        f"Successfully fetched {len(cls._rates_cache)} exchange rates"
                    )
                else:
                    logger.warning("API returned unsuccessful result")
                    cls._use_fallback_rates()
            else:
                logger.warning(
                    f"Failed to fetch exchange rates: HTTP {response.status_code}"
                )
                cls._use_fallback_rates()
                
        except requests.RequestException as e:
            logger.warning(f"Error fetching exchange rates: {e}")
            cls._use_fallback_rates()
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rates: {e}")
            cls._use_fallback_rates()
    
    @classmethod
    def _use_fallback_rates(cls) -> None:
        """Use fallback rates when API is unavailable."""
        fallback_rates = cls._load_fallback_rates()
        cls._rates_cache = fallback_rates.copy()
        cls._cache_timestamp = datetime.now()
        logger.info("Using fallback exchange rates")
    
    @classmethod
    def _get_fallback_rate(
        cls,
        from_currency: str,
        to_currency: str
    ) -> Optional[float]:
        """
        Get exchange rate from fallback rates.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate, or None if not available
        """
        fallback_rates = cls._load_fallback_rates()
        
        if from_currency in fallback_rates and to_currency in fallback_rates:
            from_rate = fallback_rates[from_currency]
            to_rate = fallback_rates[to_currency]
            return to_rate / from_rate
        
        logger.error(
            f"No fallback rate available for {from_currency} to {to_currency}"
        )
        return None
    
    @classmethod
    def get_exchange_rate(
        cls,
        from_currency: str,
        to_currency: str
    ) -> Optional[float]:
        """
        Get exchange rate from one currency to another.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate, or None if not available
        """
        # Check if cache is valid
        if cls._should_refresh_cache():
            cls._fetch_exchange_rates(from_currency)
        
        # Try to get rate from cache
        if from_currency in cls._rates_cache and to_currency in cls._rates_cache:
            # Convert via USD as base
            from_rate = cls._rates_cache[from_currency]
            to_rate = cls._rates_cache[to_currency]
            return to_rate / from_rate
        
        # Fallback to hardcoded rates
        logger.warning("Using fallback exchange rates")
        return cls._get_fallback_rate(from_currency, to_currency)
    
    @classmethod
    def get_currency_symbol(cls, currency_code: str) -> str:
        """
        Get currency symbol for a currency code.
        
        Args:
            currency_code: Currency code (e.g., 'USD')
            
        Returns:
            Currency symbol (e.g., '$')
        """
        symbols = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "INR": "₹",
            "JPY": "¥",
            "CNY": "¥",
            "AED": "د.إ",
            "CAD": "C$",
            "AUD": "A$",
            "SGD": "S$",
            "CHF": "CHF",
            "NZD": "NZ$",
            "HKD": "HK$",
            "KRW": "₩",
            "MXN": "$",
            "BRL": "R$",
            "ZAR": "R",
            "THB": "฿",
            "MYR": "RM",
        }
        
        return symbols.get(currency_code.upper(), currency_code)
    
    @classmethod
    def format_price(
        cls,
        amount: float,
        currency_code: str,
        show_code: bool = True
    ) -> str:
        """
        Format price with currency symbol and code.
        
        Args:
            amount: Amount to format
            currency_code: Currency code
            show_code: Whether to show currency code
            
        Returns:
            Formatted price string
        """
        symbol = cls.get_currency_symbol(currency_code)
        
        if show_code:
            return f"{symbol}{amount:,.2f} {currency_code}"
        else:
            return f"{symbol}{amount:,.2f}"


# Tool function for currency conversion
def convert_currency(
    amount: float,
    source_currency: str,
    target_currency: str
) -> float:
    """
    Convert amount from source currency to target currency.
    
    This is the main tool function that can be called by agents or used directly.
    
    Args:
        amount: Amount to convert
        source_currency: Source currency code (e.g., 'USD', 'EUR', 'GBP')
        target_currency: Target currency code (e.g., 'INR', 'JPY', 'AED')
        
    Returns:
        Converted amount in target currency
        
    Raises:
        ValueError: If conversion fails or currencies are not supported
        
    Example:
        >>> convert_currency(100, "USD", "INR")
        8312.0
        
        >>> convert_currency(1000, "EUR", "GBP")
        859.78
    """
    # Normalize currency codes to uppercase
    source_currency = source_currency.upper()
    target_currency = target_currency.upper()
    
    # If currencies are the same, no conversion needed
    if source_currency == target_currency:
        logger.debug(f"No conversion needed: {source_currency} == {target_currency}")
        return amount
    
    # Get exchange rate
    rate = CurrencyConverterTool.get_exchange_rate(source_currency, target_currency)
    
    if rate is None:
        error_msg = f"Could not get exchange rate for {source_currency} to {target_currency}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Convert amount
    converted_amount = amount * rate
    
    logger.debug(
        f"Converted {amount:.2f} {source_currency} to "
        f"{converted_amount:.2f} {target_currency} (rate: {rate:.4f})"
    )
    
    return round(converted_amount, 2)


def get_currency_symbol(currency_code: str) -> str:
    """
    Get currency symbol for a currency code.
    
    Args:
        currency_code: Currency code (e.g., 'USD', 'EUR', 'INR')
        
    Returns:
        Currency symbol (e.g., '$', '€', '₹')
        
    Example:
        >>> get_currency_symbol("USD")
        '$'
        
        >>> get_currency_symbol("INR")
        '₹'
    """
    return CurrencyConverterTool.get_currency_symbol(currency_code)


def format_price(amount: float, currency_code: str, show_code: bool = True) -> str:
    """
    Format price with currency symbol and optionally currency code.
    
    Args:
        amount: Amount to format
        currency_code: Currency code (e.g., 'USD', 'EUR')
        show_code: Whether to show currency code (default: True)
        
    Returns:
        Formatted price string
        
    Example:
        >>> format_price(1234.56, "USD")
        '$1,234.56 USD'
        
        >>> format_price(1234.56, "INR", show_code=False)
        '₹1,234.56'
    """
    return CurrencyConverterTool.format_price(amount, currency_code, show_code)


# Example usage and testing
if __name__ == "__main__":
    print("🧪 CURRENCY CONVERTER TOOL TEST")
    print("=" * 50)
    
    # Test conversions
    test_cases = [
        (100, "USD", "EUR"),
        (100, "USD", "GBP"),
        (100, "USD", "INR"),
        (1000, "EUR", "USD"),
        (5000, "INR", "USD"),
        (500, "GBP", "AED"),
    ]
    
    print("\n💱 Currency Conversions:")
    for amount, from_cur, to_cur in test_cases:
        try:
            converted = convert_currency(amount, from_cur, to_cur)
            formatted_from = format_price(amount, from_cur)
            formatted_to = format_price(converted, to_cur)
            print(f"{formatted_from} = {formatted_to}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    print("\n💱 Currency Symbols:")
    for code in ["USD", "EUR", "GBP", "INR", "JPY", "AED"]:
        symbol = get_currency_symbol(code)
        formatted = format_price(1234.56, code)
        print(f"{code}: {symbol} → {formatted}")
    
    print("\n✅ Tool test completed!")
