"""
Currency Converter Tool

This tool provides currency conversion functionality for flight prices.
Can be used as a standalone function or by AI agents for currency conversion.
Fetches real-time exchange rates from API only.
"""

import requests
from typing import Dict, Optional
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class CurrencyConverterTool:
    """
    Currency converter tool using real-time API calls.
    
    Uses exchangerate-api.com for live exchange rates.
    """

    @classmethod
    def _fetch_exchange_rates(cls, base_currency: str = "USD") -> Dict[str, float]:
        """
        Fetch current exchange rates from API.
        
        Args:
            base_currency: Base currency for rates (default: USD)
            
        Returns:
            Dictionary of currency codes to rates
            
        Raises:
            Exception: If API call fails
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
                    rates = data.get("rates", {})
                    logger.debug(f"Successfully fetched {len(rates)} exchange rates")
                    return rates
                else:
                    error_msg = f"API returned unsuccessful result: {data.get('error-type', 'unknown error')}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"Failed to fetch exchange rates: HTTP {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            error_msg = f"Error fetching exchange rates: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    @classmethod
    def get_exchange_rate(
        cls,
        from_currency: str,
        to_currency: str
    ) -> float:
        """
        Get exchange rate from one currency to another using real-time API.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate
            
        Raises:
            Exception: If API call fails or currencies not found
        """
        # Fetch fresh rates from API
        rates = cls._fetch_exchange_rates(from_currency)
        
        # Try to get rate from response
        if from_currency in rates and to_currency in rates:
            # Convert via base currency
            from_rate = rates[from_currency]
            to_rate = rates[to_currency]
            return to_rate / from_rate
        
        # If conversion is direct (from base currency)
        if to_currency in rates:
            return rates[to_currency]
        
        error_msg = f"Exchange rate not available for {from_currency} to {to_currency}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
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
    Convert amount from source currency to target currency using real-time rates.
    
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
    
    try:
        # Get exchange rate from API
        rate = CurrencyConverterTool.get_exchange_rate(source_currency, target_currency)
        
        # Convert amount
        converted_amount = amount * rate
        
        logger.debug(
            f"Converted {amount:.2f} {source_currency} to "
            f"{converted_amount:.2f} {target_currency} (rate: {rate:.4f})"
        )
        
        return round(converted_amount, 2)
    except Exception as e:
        error_msg = f"Could not get exchange rate for {source_currency} to {target_currency}: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)


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
