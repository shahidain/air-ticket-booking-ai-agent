"""
Amadeus API Client for flight search and booking operations.

This client handles:
1. Authentication with Amadeus API
2. Flight search with flexible date options
3. Finding cheaper alternatives (±1 day)
4. Flight booking operations
"""

from amadeus import Client, ResponseError
from typing import List, Optional
from datetime import datetime, timedelta
from models.flight_models import (
    FlightSearchRequest,
    FlightSearchResponse,
    FlightOffer,
    FlightSegment,
    AlternativeDateOffer,
    BookingRequest,
    BookingConfirmation,
    PassengerInfo
)
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AmadeusClient:
    """Client for interacting with Amadeus Flight API."""

    def __init__(self):
        """Initialize Amadeus client with credentials from config."""
        try:
            self.client = Client(
                client_id=settings.amadeus_api_key,
                client_secret=settings.amadeus_api_secret,
                hostname=settings.amadeus_hostname
            )
            logger.info("Amadeus client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Amadeus client: {e}")
            raise

    def search_flights(self, request: FlightSearchRequest) -> FlightSearchResponse:
        """
        Search for flights and find cheaper alternatives on nearby dates.

        Args:
            request: Flight search parameters

        Returns:
            FlightSearchResponse with original and alternative date offers

        Raises:
            ResponseError: If Amadeus API returns an error
        """
        logger.info(
            f"Searching flights from {request.origin} to {request.destination} "
            f"on {request.departure_date}"
        )

        try:
            # Search flights for the requested date
            original_offers = self._search_flights_for_date(request)

            # Search for cheaper alternatives (1 day before and after)
            alternative_offers = self._search_alternative_dates(request, original_offers)

            response = FlightSearchResponse(
                original_date_offers=original_offers,
                alternative_offers=alternative_offers
            )

            logger.info(
                f"Found {len(original_offers)} flights for requested date, "
                f"{len(alternative_offers)} alternative date options"
            )

            return response

        except ResponseError as error:
            logger.error(f"Amadeus API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error during flight search: {e}")
            raise

    def _search_flights_for_date(
        self,
        request: FlightSearchRequest
    ) -> List[FlightOffer]:
        """
        Search flights for a specific date.

        Args:
            request: Flight search parameters

        Returns:
            List of flight offers
        """
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=request.origin,
                destinationLocationCode=request.destination,
                departureDate=request.departure_date.isoformat(),
                adults=request.adults,
                travelClass=request.travel_class,
                max=request.max_results
            )

            # Parse the response into our models
            offers = []
            for offer_data in response.data:
                offer = self._parse_flight_offer(offer_data)
                if offer:
                    offers.append(offer)

            return offers

        except ResponseError as error:
            logger.warning(f"No flights found for {request.departure_date}: {error}")
            return []

    def _search_alternative_dates(
        self,
        request: FlightSearchRequest,
        original_offers: List[FlightOffer]
    ) -> List[AlternativeDateOffer]:
        """
        Search for cheaper flights on dates ±1 day from requested date.

        Args:
            request: Original flight search request
            original_offers: Offers found for the original date

        Returns:
            List of alternative date offers that are cheaper
        """
        if not original_offers:
            return []

        # Get the cheapest price from original date
        min_original_price = min(offer.price for offer in original_offers)

        alternative_offers = []

        # Check day before and day after
        for day_offset in [-1, 1]:
            alternative_date = request.departure_date + timedelta(days=day_offset)

            # Create new request for alternative date
            alt_request = request.model_copy()
            alt_request.departure_date = alternative_date

            # Search flights for alternative date
            alt_offers = self._search_flights_for_date(alt_request)

            if alt_offers:
                # Get cheapest price for this date
                min_alt_price = min(offer.price for offer in alt_offers)

                # Only include if it's cheaper
                if min_alt_price < min_original_price:
                    price_diff = min_alt_price - min_original_price

                    alternative_offers.append(
                        AlternativeDateOffer(
                            departure_date=alternative_date,
                            offers=alt_offers[:3],  # Top 3 cheapest
                            price_difference=price_diff
                        )
                    )

        return alternative_offers

    def _parse_flight_offer(self, offer_data: dict) -> Optional[FlightOffer]:
        """
        Parse raw Amadeus API response into FlightOffer model.

        Args:
            offer_data: Raw flight offer data from Amadeus

        Returns:
            FlightOffer object or None if parsing fails
        """
        try:
            # Extract price information
            price = float(offer_data['price']['total'])
            currency = offer_data['price']['currency']

            # Parse itineraries (usually one for one-way)
            segments = []
            total_duration = "0h 0m"
            number_of_stops = 0

            for itinerary in offer_data['itineraries']:
                total_duration = itinerary.get('duration', 'PT0H0M')
                total_duration = self._format_duration(total_duration)

                for segment_data in itinerary['segments']:
                    segment = self._parse_segment(segment_data, offer_data)
                    if segment:
                        segments.append(segment)
                        number_of_stops += 1

            number_of_stops = max(0, number_of_stops - 1)  # Stops = segments - 1

            # Get booking class
            booking_class = offer_data['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin']

            # Get available seats
            available_seats = offer_data['numberOfBookableSeats']

            return FlightOffer(
                id=offer_data['id'],
                price=price,
                currency=currency,
                segments=segments,
                total_duration=total_duration,
                number_of_stops=number_of_stops,
                booking_class=booking_class,
                available_seats=available_seats
            )

        except Exception as e:
            logger.warning(f"Failed to parse flight offer: {e}")
            return None

    def _parse_segment(self, segment_data: dict, offer_data: dict) -> Optional[FlightSegment]:
        """Parse a single flight segment."""
        try:
            # Get carrier information
            carrier_code = segment_data['carrierCode']
            flight_number = segment_data['number']

            # Extract carrier name from dictionaries in the response
            carrier_name = carrier_code  # Default to code
            if 'dictionaries' in offer_data and 'carriers' in offer_data['dictionaries']:
                carrier_name = offer_data['dictionaries']['carriers'].get(
                    carrier_code,
                    carrier_code
                )

            # Parse times
            departure_time = segment_data['departure']['at']
            arrival_time = segment_data['arrival']['at']

            # Duration
            duration = self._format_duration(segment_data.get('duration', 'PT0H0M'))

            return FlightSegment(
                departure_airport=segment_data['departure']['iataCode'],
                arrival_airport=segment_data['arrival']['iataCode'],
                departure_time=departure_time,
                arrival_time=arrival_time,
                duration=duration,
                carrier_code=carrier_code,
                carrier_name=carrier_name,
                flight_number=flight_number,
                aircraft=segment_data.get('aircraft', {}).get('code')
            )

        except Exception as e:
            logger.warning(f"Failed to parse segment: {e}")
            return None

    @staticmethod
    def _format_duration(iso_duration: str) -> str:
        """
        Convert ISO 8601 duration to human-readable format.

        Args:
            iso_duration: Duration in ISO format (e.g., 'PT2H30M')

        Returns:
            Formatted duration (e.g., '2h 30m')
        """
        try:
            # Remove 'PT' prefix
            duration = iso_duration.replace('PT', '')

            hours = 0
            minutes = 0

            if 'H' in duration:
                hours = int(duration.split('H')[0])
                duration = duration.split('H')[1]

            if 'M' in duration:
                minutes = int(duration.replace('M', ''))

            return f"{hours}h {minutes}m"

        except Exception:
            return iso_duration

    def book_flight(self, booking_request: BookingRequest) -> BookingConfirmation:
        """
        Book a flight with passenger information.

        Note: This is a simplified implementation. In production, you would need:
        - Flight price confirmation before booking
        - Payment processing integration
        - More detailed passenger validation

        Args:
            booking_request: Booking details with offer ID and passenger info

        Returns:
            BookingConfirmation with booking reference

        Raises:
            ResponseError: If booking fails
        """
        logger.info(f"Attempting to book flight offer: {booking_request.offer_id}")

        try:
            # In a real implementation, you would:
            # 1. Confirm the price using flight-offers-pricing
            # 2. Create the flight order using flight-orders
            #
            # For this demo, we'll simulate a booking response
            # since actual booking requires payment integration

            # Simulated booking response
            booking_ref = f"PNR{datetime.now().strftime('%Y%m%d%H%M%S')}"

            logger.warning(
                "⚠️  DEMO MODE: Actual flight booking requires payment integration. "
                "Returning simulated booking confirmation."
            )

            # In production, use this pattern:
            # response = self.client.booking.flight_orders.post(flight_order_data)

            return BookingConfirmation(
                booking_reference=booking_ref,
                status="CONFIRMED",
                total_price=0.0,  # Would come from actual booking
                currency="USD",
                flight_offer=None,  # Would include the booked offer
                passengers=booking_request.passengers,
                booking_date=datetime.now()
            )

        except ResponseError as error:
            logger.error(f"Booking failed: {error}")
            raise
        except Exception as e:
            logger.error(f"Error during booking: {e}")
            raise

    def get_airport_city(self, iata_code: str) -> str:
        """
        Get city name for an airport IATA code.

        Args:
            iata_code: Airport IATA code (e.g., 'JFK')

        Returns:
            City name
        """
        try:
            response = self.client.reference_data.locations.get(
                keyword=iata_code,
                subType='AIRPORT'
            )

            if response.data:
                return response.data[0]['address']['cityName']

            return iata_code

        except Exception as e:
            logger.warning(f"Could not fetch city for {iata_code}: {e}")
            return iata_code
