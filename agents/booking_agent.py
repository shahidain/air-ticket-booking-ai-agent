"""
Agent 3: Booking Agent

This agent:
1. Receives user's selected flight from Agent 2
2. Collects passenger information (or uses defaults for demo)
3. Initiates booking through Amadeus API
4. Handles booking confirmation
5. Passes booking details to next agent for ticket generation
"""

from typing import Dict, Any, List
from datetime import date
from api.amadeus_client import AmadeusClient
from models.flight_models import (
    BookingRequest,
    BookingConfirmation,
    PassengerInfo,
    FlightOffer
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BookingAgent:
    """
    Agent 3: Handles flight booking operations.

    This agent takes the user's selection and completes the booking process.
    """

    def __init__(self):
        """Initialize the agent with Amadeus client."""
        self.amadeus_client = AmadeusClient()
        logger.info("Booking Agent initialized")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the booking agent logic.

        Args:
            state: Current workflow state with selected flight

        Returns:
            Updated state with booking confirmation
        """
        logger.info("Booking Agent executing")

        try:
            # Extract selected offer from state
            selected_offer = FlightOffer.model_validate(state["selected_offer"])

            # Collect passenger information
            passengers = self._collect_passenger_info(state)

            # Create booking request
            booking_request = BookingRequest(
                offer_id=selected_offer.id,
                passengers=passengers
            )

            # Attempt to book the flight
            print("\n🔄 Processing your booking...")
            booking_confirmation = self.amadeus_client.book_flight(booking_request)

            # Update confirmation with actual flight offer details
            booking_confirmation.flight_offer = selected_offer
            booking_confirmation.total_price = selected_offer.price
            booking_confirmation.currency = selected_offer.currency

            # Store in state
            state["booking_confirmation"] = booking_confirmation.model_dump()
            state["passengers"] = [p.model_dump() for p in passengers]

            logger.info(
                f"Booking completed successfully. Reference: {booking_confirmation.booking_reference}"
            )

            print(f"\n✅ Booking confirmed! Reference: {booking_confirmation.booking_reference}")

            return state

        except Exception as e:
            logger.error(f"Error in Booking Agent: {e}")
            state["error"] = str(e)
            print(f"\n❌ Booking failed: {e}")
            raise

    def _collect_passenger_info(self, state: Dict[str, Any]) -> List[PassengerInfo]:
        """
        Collect passenger information from user or use defaults.

        In a production system, this would:
        - Prompt for each passenger's details
        - Validate passport information
        - Verify email and phone
        - Store in secure database

        For this demo, we'll use simplified input.

        Args:
            state: Current workflow state

        Returns:
            List of PassengerInfo objects
        """
        # Get number of passengers from original request
        adults = state.get("parsed_request", {}).get("adults", 1)

        passengers = []

        print("\n" + "="*70)
        print("PASSENGER INFORMATION")
        print("="*70)
        print("Please enter passenger details:")
        print("💡 Tip: You can type 'cancel' at any time to exit the program")
        print()

        for i in range(adults):
            print(f"Passenger {i + 1}:")

            # Basic information
            first_name = input("  First Name (or 'cancel' to exit): ").strip()
            if first_name.lower() in ['cancel', 'exit', 'quit']:
                print("\n🚪 Booking cancelled by user. Thank you for using AI Ticket Booking!")
                raise KeyboardInterrupt("User cancelled during passenger information collection")
            first_name = first_name or "John"
            
            last_name = input("  Last Name: ").strip() or "Doe"
            gender = input("  Gender (M/F): ").strip().upper() or "M"
            email = input("  Email: ").strip() or "john.doe@example.com"
            phone = input("  Phone: ").strip() or "+91-1234567890"

            # Government ID Information
            print("\n  Government ID (Default: AADHAAR)")
            print("  Options: 1=AADHAAR, 2=PASSPORT, 3=DRIVING_LICENSE")
            id_choice = input("  Select ID Type (1/2/3) [1]: ").strip() or "1"

            id_type_map = {
                "1": "AADHAAR",
                "2": "PASSPORT",
                "3": "DRIVING_LICENSE"
            }
            id_type = id_type_map.get(id_choice, "AADHAAR")

            # Get ID number with format validation
            if id_type == "AADHAAR":
                id_number = self._get_aadhaar_number()
            else:
                id_number = input(f"  {id_type} Number: ").strip() or "DEFAULT123456"

            passenger = PassengerInfo(
                first_name=first_name,
                last_name=last_name,
                gender=gender if gender in ["M", "F"] else "M",
                email=email,
                phone=phone,
                id_type=id_type,
                id_number=id_number
            )

            passengers.append(passenger)
            print()

        logger.info(f"Collected information for {len(passengers)} passenger(s)")

        return passengers

    def _get_aadhaar_number(self) -> str:
        """
        Get and validate Aadhaar number in format: 0000-0000-0000

        Returns:
            Formatted Aadhaar number
        """
        while True:
            aadhaar = input("  AADHAAR Number (12 digits) [Press Enter for demo]: ").strip()

            # Default for demo
            if not aadhaar:
                return "1234-5678-9012"

            # Remove any existing hyphens or spaces
            aadhaar_digits = aadhaar.replace("-", "").replace(" ", "")

            # Validate: must be exactly 12 digits
            if len(aadhaar_digits) == 12 and aadhaar_digits.isdigit():
                # Format as 0000-0000-0000
                formatted = f"{aadhaar_digits[:4]}-{aadhaar_digits[4:8]}-{aadhaar_digits[8:]}"
                print(f"  ✓ Formatted: {formatted}")
                return formatted
            else:
                print("  ❌ Invalid! AADHAAR must be 12 digits. Example: 1234-5678-9012")
                print("     You can enter with or without hyphens.")

    def _use_demo_passengers(self, num_passengers: int = 1) -> List[PassengerInfo]:
        """
        Create demo passenger info for testing.

        Args:
            num_passengers: Number of passengers to create

        Returns:
            List of PassengerInfo with demo data
        """
        demo_passengers = []

        for i in range(num_passengers):
            passenger = PassengerInfo(
                first_name=f"Passenger{i + 1}",
                last_name="Demo",
                gender="M",
                email=f"passenger{i + 1}@demo.com",
                phone="+91-1234567890",
                id_type="AADHAAR",
                id_number=f"1234-5678-{9000+i:04d}"
            )
            demo_passengers.append(passenger)

        return demo_passengers


# Example usage for testing
if __name__ == "__main__":
    # Mock state for testing
    from datetime import datetime

    mock_offer = {
        "id": "DEMO123",
        "price": 299.99,
        "currency": "USD",
        "segments": [],
        "total_duration": "5h 30m",
        "number_of_stops": 0,
        "booking_class": "ECONOMY",
        "available_seats": 5
    }

    mock_state = {
        "selected_offer": mock_offer,
        "parsed_request": {
            "adults": 1
        }
    }

    agent = BookingAgent()
    print("Booking Agent ready for testing")
    # Uncomment to test:
    # result = agent.execute(mock_state)
