"""
Agent 4: Ticket Generation Agent

This agent:
1. Receives booking confirmation from Agent 3
2. Uses LLM to generate professional ticket document
3. Formats flight details, passenger info, and booking reference
4. Creates a ticket-style presentation
5. Passes formatted ticket to final notification agent
"""

from typing import Dict, Any
from api.openai_client import OpenAIClient
from models.flight_models import BookingConfirmation, FlightOffer, PassengerInfo
from utils.logger import setup_logger
from tools.currency_converter_tool import convert_currency, get_currency_symbol
from config import settings

logger = setup_logger(__name__)


class TicketGenerationAgent:
    """
    Agent 4: Generates formatted ticket documents.

    This agent takes booking confirmation data and creates
    a professional, human-readable ticket format.
    """

    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.openai_client = OpenAIClient()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the ticket generation agent logic.

        Args:
            state: Current workflow state with booking confirmation

        Returns:
            Updated state with formatted ticket
        """
        logger.debug("Ticket Generation Agent executing")

        try:
            # Extract booking confirmation from state
            booking_confirmation = BookingConfirmation.model_validate(
                state["booking_confirmation"]
            )

            # Generate formatted ticket
            formatted_ticket = self._generate_ticket(booking_confirmation)

            # Store in state
            state["formatted_ticket"] = formatted_ticket

            logger.debug("Ticket generated successfully")

            return state

        except Exception as e:
            logger.error(f"Error in Ticket Generation Agent: {e}")
            state["error"] = str(e)
            raise

    def _generate_ticket(self, booking: BookingConfirmation) -> str:
        """
        Generate a professional ticket document using LLM.

        Args:
            booking: Booking confirmation with all details

        Returns:
            Formatted ticket as string
        """
        # Prepare structured data for ticket generation
        ticket_data = self._prepare_ticket_data(booking)

        # Use LLM to format the ticket
        format_instruction = """You are a professional ticket generation system. Create a beautifully formatted airline ticket.

Your ticket should include:

1. **HEADER**: "✈️ E-TICKET / BOARDING PASS"
2. **Booking Reference**: Large, prominent PNR
3. **Booking Status**: Confirmed/Pending
4. **Passenger Information**:
   - Name(s)
   - Government ID Type and Number
   - Email
   - Phone
5. **Flight Details**:
   - Carrier name and flight number(s)
   - Route (Origin → Destination with full airport names)
   - Departure date and time
   - Arrival date and time
   - Duration
   - Number of stops
   - Booking class
6. **Price Breakdown** (IMPORTANT - Show all three lines):
   - Base Fare: [amount]
   - GST ([rate]): [amount]
   - Total Amount: [amount] (in bold or highlighted)
   - Booking date
7. **Important Information Section**:
   - Check-in opens 24 hours before departure
   - Arrive at airport 2-3 hours before international flights
   - Valid ID required
   - Baggage allowance info

Format it to look like a real airline ticket with clear sections, borders made with characters like ═, ║, ─.
Use emojis appropriately for visual appeal.

Make it professional and easy to read. Use proper spacing and alignment.
IMPORTANT: Always show the price breakdown with base fare, GST amount, and total separately."""

        formatted_ticket = self.openai_client.format_response(
            data=ticket_data,
            format_instruction=format_instruction,
            temperature=0.5  # Moderate creativity while maintaining structure
        )

        return formatted_ticket

    def _prepare_ticket_data(self, booking: BookingConfirmation) -> Dict[str, Any]:
        """
        Prepare booking data in structured format for ticket generation.

        Args:
            booking: Booking confirmation object

        Returns:
            Dictionary with organized ticket data
        """
        flight = booking.flight_offer

        # Convert currency if needed
        display_price = booking.total_price
        display_currency = booking.currency

        if settings.enable_currency_conversion and settings.local_currency != booking.currency:
            try:
                display_price = convert_currency(
                    booking.total_price,
                    booking.currency,
                    settings.local_currency
                )
                display_currency = settings.local_currency
            except Exception as e:
                logger.warning(f"Currency conversion failed, using original currency: {e}")

        # Calculate GST
        gst_amount = round(display_price * (settings.gst_rate / 100), 2)
        total_with_gst = round(display_price + gst_amount, 2)

        currency_symbol = get_currency_symbol(display_currency)

        # Get route information
        first_segment = flight.segments[0]
        last_segment = flight.segments[-1]

        # Format passenger list
        passengers_formatted = []
        for passenger in booking.passengers:
            passengers_formatted.append({
                "name": f"{passenger.first_name} {passenger.last_name}",
                "gender": passenger.gender,
                "id_type": passenger.id_type,
                "id_number": passenger.id_number,
                "email": passenger.email,
                "phone": passenger.phone
            })

        # Format flight segments with full carrier name and code
        segments_formatted = []
        for i, segment in enumerate(flight.segments, start=1):
            segments_formatted.append({
                "segment_number": i,
                "carrier": f"{segment.carrier_name} ({segment.carrier_code})",
                "carrier_full": segment.carrier_name,
                "carrier_code": segment.carrier_code,
                "flight_number": segment.flight_number,
                "from": f"{segment.departure_airport}",
                "to": f"{segment.arrival_airport}",
                "departure": segment.departure_time,
                "arrival": segment.arrival_time,
                "duration": segment.duration,
                "aircraft": segment.aircraft or "N/A"
            })

        ticket_data = {
            "booking_reference": booking.booking_reference,
            "status": booking.status,
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M:%S"),
            "passengers": passengers_formatted,
            "route": f"{first_segment.departure_airport} → {last_segment.arrival_airport}",
            "segments": segments_formatted,
            "total_duration": flight.total_duration,
            "stops": flight.number_of_stops,
            "booking_class": flight.booking_class,
            "base_fare": f"{currency_symbol}{display_price:.2f} {display_currency}",
            "gst_rate": f"{settings.gst_rate}%",
            "gst_amount": f"{currency_symbol}{gst_amount:.2f} {display_currency}",
            "total_price": f"{currency_symbol}{total_with_gst:.2f} {display_currency}",
            "carrier_summary": flight.get_carrier_names()
        }

        return ticket_data


# Example usage for testing
if __name__ == "__main__":
    from datetime import datetime, date

    # Mock booking confirmation for testing
    mock_booking = {
        "booking_reference": "ABC123XYZ",
        "status": "CONFIRMED",
        "total_price": 599.99,
        "currency": "USD",
        "booking_date": datetime.now(),
        "flight_offer": {
            "id": "DEMO123",
            "price": 599.99,
            "currency": "USD",
            "total_duration": "5h 30m",
            "number_of_stops": 0,
            "booking_class": "ECONOMY",
            "available_seats": 5,
            "segments": [
                {
                    "departure_airport": "JFK",
                    "arrival_airport": "LAX",
                    "departure_time": "2025-11-15T08:00:00",
                    "arrival_time": "2025-11-15T11:30:00",
                    "duration": "5h 30m",
                    "carrier_code": "AA",
                    "carrier_name": "American Airlines",
                    "flight_number": "100",
                    "aircraft": "Boeing 737"
                }
            ]
        },
        "passengers": [
            {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": date(1990, 1, 1),
                "gender": "M",
                "email": "john.doe@example.com",
                "phone": "+1234567890"
            }
        ]
    }

    mock_state = {
        "booking_confirmation": mock_booking
    }

    agent = TicketGenerationAgent()
    print("Ticket Generation Agent ready for testing")
    # Uncomment to test:
    # result = agent.execute(mock_state)
    # print(result["formatted_ticket"])
