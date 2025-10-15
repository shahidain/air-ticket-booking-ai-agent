"""
Data models for flight information and booking.

These Pydantic models ensure type safety and validation throughout the application.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time


class FlightSegment(BaseModel):
    """Represents a single flight segment."""

    departure_airport: str = Field(description="IATA code of departure airport")
    arrival_airport: str = Field(description="IATA code of arrival airport")
    departure_time: str = Field(description="Departure date and time")
    arrival_time: str = Field(description="Arrival date and time")
    duration: str = Field(description="Flight duration (e.g., '2h 30m')")
    carrier_code: str = Field(description="Airline carrier code")
    carrier_name: str = Field(description="Airline carrier name")
    flight_number: str = Field(description="Flight number")
    aircraft: Optional[str] = Field(default=None, description="Aircraft type")


class FlightOffer(BaseModel):
    """Represents a complete flight offer with pricing."""

    id: str = Field(description="Unique identifier for the flight offer")
    price: float = Field(description="Total price in the specified currency")
    currency: str = Field(default="USD", description="Currency code")
    segments: List[FlightSegment] = Field(description="List of flight segments")
    total_duration: str = Field(description="Total journey duration")
    number_of_stops: int = Field(description="Number of stops (0 for direct)")
    booking_class: str = Field(description="Booking class (Economy, Business, etc.)")
    available_seats: Optional[int] = Field(default=None, description="Number of available seats")

    def get_carrier_names(self) -> str:
        """Get comma-separated list of unique carrier names."""
        carriers = list(set(segment.carrier_name for segment in self.segments))
        return ", ".join(carriers)
    
    def convert_currency(self, target_currency: str) -> Optional['FlightOffer']:
        """
        Convert flight offer price to target currency.
        
        Args:
            target_currency: Target currency code
            
        Returns:
            New FlightOffer with converted price, or None if conversion fails
        """
        from tools.currency_converter_tool import convert_currency
        
        if self.currency == target_currency:
            return self
        
        try:
            converted_price = convert_currency(
                self.price,
                self.currency,
                target_currency
            )
            
            # Create a copy with converted price
            offer_dict = self.model_dump()
            offer_dict['price'] = converted_price
            offer_dict['currency'] = target_currency
            
            return FlightOffer.model_validate(offer_dict)
        except ValueError:
            return None
    
    def get_formatted_price(self, show_code: bool = True) -> str:
        """
        Get formatted price with currency symbol.

        Args:
            show_code: Whether to show currency code

        Returns:
            Formatted price string
        """
        from tools.currency_converter_tool import format_price

        return format_price(self.price, self.currency, show_code)

    def calculate_gst(self, gst_rate: float) -> float:
        """
        Calculate GST amount on the base price.

        Args:
            gst_rate: GST rate in percentage (e.g., 18.0 for 18%)

        Returns:
            GST amount
        """
        return round(self.price * (gst_rate / 100), 2)

    def get_total_with_gst(self, gst_rate: float) -> float:
        """
        Calculate total price including GST.

        Args:
            gst_rate: GST rate in percentage (e.g., 18.0 for 18%)

        Returns:
            Total price including GST
        """
        return round(self.price + self.calculate_gst(gst_rate), 2)


class FlightSearchRequest(BaseModel):
    """Request parameters for flight search."""

    origin: str = Field(description="Origin airport IATA code")
    destination: str = Field(description="Destination airport IATA code")
    departure_date: date = Field(description="Departure date")
    departure_time: Optional[time] = Field(default=None, description="Preferred departure time")
    adults: int = Field(default=1, description="Number of adult passengers")
    travel_class: str = Field(default="ECONOMY", description="Travel class")
    max_results: int = Field(default=10, description="Maximum number of results")


class AlternativeDateOffer(BaseModel):
    """Flight offers for alternative dates (cheaper options)."""

    departure_date: date = Field(description="Alternative departure date", alias="date")
    offers: List[FlightOffer] = Field(description="Flight offers for this date")
    price_difference: float = Field(description="Price difference compared to original date")

    model_config = {"populate_by_name": True}


class FlightSearchResponse(BaseModel):
    """Complete response from flight search including alternatives."""

    original_date_offers: List[FlightOffer] = Field(description="Offers for requested date")
    alternative_offers: List[AlternativeDateOffer] = Field(
        default_factory=list,
        description="Cheaper offers for nearby dates"
    )


class PassengerInfo(BaseModel):
    """Passenger information for booking."""

    first_name: str
    last_name: str
    gender: str = Field(description="M or F")
    email: str
    phone: str

    # Government ID Information
    id_type: str = Field(default="AADHAAR", description="ID type: AADHAAR, PASSPORT, DRIVING_LICENSE")
    id_number: str = Field(description="Government ID number")

    # Optional fields
    nationality: Optional[str] = None


class BookingRequest(BaseModel):
    """Request to book a flight."""

    offer_id: str = Field(description="ID of the selected flight offer")
    passengers: List[PassengerInfo] = Field(description="List of passengers")


class BookingConfirmation(BaseModel):
    """Confirmation details after successful booking."""

    booking_reference: str = Field(description="PNR/Booking reference number")
    status: str = Field(description="Booking status")
    total_price: float
    currency: str
    flight_offer: Optional[FlightOffer] = None
    passengers: List[PassengerInfo]
    booking_date: datetime = Field(default_factory=datetime.now)
