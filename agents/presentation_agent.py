"""
Agent 2: Flight Presentation Agent

This agent:
1. Receives flight search results from Agent 1
2. Formats flight offers into user-friendly presentation
3. Shows carrier names, flight times, duration, and prices
4. Highlights cheaper alternatives on nearby dates
5. Asks user to select an option
6. Waits for user input and validates selection
"""

from typing import Dict, Any, List
import re
from api.openai_client import OpenAIClient
from models.flight_models import FlightSearchResponse, FlightOffer, AlternativeDateOffer
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FlightPresentationAgent:
    """
    Agent 2: Formats and presents flight options to user.

    This agent takes raw flight data and creates human-readable
    presentations using LLM for natural language generation.
    """

    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.openai_client = OpenAIClient()
        logger.info("Flight Presentation Agent initialized")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the flight presentation agent logic.

        Args:
            state: Current workflow state with flight results

        Returns:
            Updated state with formatted presentation
        """
        logger.info("Flight Presentation Agent executing")

        try:
            # Extract flight results from state
            flight_results = FlightSearchResponse.model_validate(state["flight_results"])
            parsed_request = state["parsed_request"]

            # Auto-detect sorting preference from user message and sort flights
            sorted_offers = self._sort_flights_by_preference(flight_results.original_date_offers, state.get("user_prompt", ""))
            flight_results.original_date_offers = sorted_offers

            # Format flights for presentation
            presentation = self._format_flight_presentation(
                flight_results,
                parsed_request
            )

            # Store presentation in state
            state["presentation"] = presentation

            # Display to user
            print("\n" + "="*70)
            print(presentation)
            print("="*70)

            logger.info("Flight presentation displayed to user")

            return state

        except Exception as e:
            logger.error(f"Error in Flight Presentation Agent: {e}")
            state["error"] = str(e)
            raise

    def _format_flight_presentation(
        self,
        flight_results: FlightSearchResponse,
        parsed_request: Dict[str, Any]
    ) -> str:
        """
        Format flight results into table format.

        Args:
            flight_results: Search results with flights
            parsed_request: Original parsed request

        Returns:
            Formatted presentation string with tables
        """
        output = []

        # Header
        output.append("\n✈️  FLIGHT SEARCH RESULTS")
        output.append(f"\nRoute: {parsed_request['origin_city']} ({parsed_request['origin_code']}) → "
                     f"{parsed_request['destination_city']} ({parsed_request['destination_code']})")
        output.append(f"Date: {parsed_request['departure_date']}")
        output.append("\n")

        # Main flights table
        if flight_results.original_date_offers:
            output.append("┌" + "─" * 130 + "┐")
            output.append(f"│ {'#':<3} │ {'Carrier':<22} │ {'Departure':<18} │ {'Arrival':<18} │ {'Duration':<10} │ {'Stops':<10} │ {'Class':<8} │ {'Price':<15} │ {'Seats':<6} │")
            output.append("├" + "─" * 130 + "┤")

            for i, offer in enumerate(flight_results.original_date_offers, start=1):
                first_segment = offer.segments[0]
                last_segment = offer.segments[-1]

                # Extract time from datetime string (YYYY-MM-DDTHH:MM:SS)
                dept_time = first_segment.departure_time.split('T')[1][:5] if 'T' in first_segment.departure_time else first_segment.departure_time
                arr_time = last_segment.arrival_time.split('T')[1][:5] if 'T' in last_segment.arrival_time else last_segment.arrival_time

                carrier = offer.get_carrier_names()[:20]  # Truncate if too long
                departure = f"{dept_time} {first_segment.departure_airport}"
                arrival = f"{arr_time} {last_segment.arrival_airport}"
                
                # Enhanced stops display
                if offer.number_of_stops == 0:
                    stops_text = "✈️ Direct"
                else:
                    stops_text = f"🔄 {offer.number_of_stops} stop{'s' if offer.number_of_stops > 1 else ''}"
                
                # Format class
                class_short = offer.booking_class[:8] if offer.booking_class else "ECONOMY"
                
                # Format price with better alignment
                price = f"{offer.currency} {offer.price:.2f}"
                
                # Available seats
                seats = str(offer.available_seats) if offer.available_seats else "N/A"

                output.append(f"│ {i:<3} │ {carrier:<22} │ {departure:<18} │ {arrival:<18} │ {offer.total_duration:<10} │ {stops_text:<10} │ {class_short:<8} │ {price:<15} │ {seats:<6} │")

            output.append("└" + "─" * 130 + "┘")
        else:
            output.append("❌ No flights found for the requested date.")

        # Alternative dates table
        if flight_results.alternative_offers:
            output.append("\n")
            output.append("💰 CHEAPER ALTERNATIVES ON NEARBY DATES")
            output.append("   (Consider these dates to save money!)")
            output.append("\n┌" + "─" * 110 + "┐")
            output.append(f"│ {'Date':<12} │ {'Day':<10} │ {'Savings':<12} │ {'Carrier':<20} │ {'Duration':<10} │ {'Stops':<10} │ {'Price':<15} │")
            output.append("├" + "─" * 110 + "┤")

            for alt in flight_results.alternative_offers:
                cheapest = min(alt.offers, key=lambda x: x.price)
                
                # Format date and day
                date_str = str(alt.departure_date)
                day_name = alt.departure_date.strftime("%A")[:9]  # Truncate long day names
                
                # Format savings with currency symbol
                savings = f"💰 -{abs(alt.price_difference):.2f}"
                
                carrier = cheapest.get_carrier_names()[:18]
                
                # Enhanced stops display
                if cheapest.number_of_stops == 0:
                    stops_text = "✈️ Direct"
                else:
                    stops_text = f"🔄 {cheapest.number_of_stops} stop{'s' if cheapest.number_of_stops > 1 else ''}"
                
                price = f"{cheapest.currency} {cheapest.price:.2f}"

                output.append(f"│ {date_str:<12} │ {day_name:<10} │ {savings:<12} │ {carrier:<20} │ {cheapest.total_duration:<10} │ {stops_text:<10} │ {price:<15} │")

            output.append("└" + "─" * 110 + "┘")
            
            # Add note about alternative dates
            output.append("\n💡 Tip: Alternative dates show flights that are cheaper than your requested date.")
            output.append("   You can book these by running the search again with the new date.")

        # Selection prompt with helpful instructions
        output.append("\n" + "═" * 70)
        output.append("📝 FLIGHT SELECTION")
        output.append("═" * 70)
        output.append("Please select a flight option by entering the number (#)")
        output.append("")
        output.append("� Available Commands:")
        output.append("   • Enter number (1-N) = Select flight")
        output.append("   • 'info X' = Get detailed info about option X")
        output.append("   • 'cancel' = Exit program")
        output.append("")
        output.append("�🔍 Flight Details Legend:")
        output.append("   • ✈️ Direct = Non-stop flight")
        output.append("   • 🔄 X stops = Flight with X connections")
        output.append("   • Seats = Available seats remaining")
        output.append("   • Times shown in 24-hour format (HH:MM)")
        output.append("")
        output.append("💡 Tip: Next time, mention preferences in your request:")
        output.append("   'Find cheapest flights...' | 'Direct flights only...' | 'Early morning flights...'")  

        return "\n".join(output)

    def _format_offers_list(self, offers: List[FlightOffer]) -> List[Dict[str, Any]]:
        """
        Convert flight offers to simple dict format for LLM.

        Args:
            offers: List of flight offers

        Returns:
            List of simplified offer dictionaries
        """
        formatted = []

        for i, offer in enumerate(offers, start=1):
            # Get first and last segment for departure/arrival
            first_segment = offer.segments[0]
            last_segment = offer.segments[-1]

            formatted.append({
                "option_number": i,
                "offer_id": offer.id,
                "carrier": offer.get_carrier_names(),
                "departure": f"{first_segment.departure_time} from {first_segment.departure_airport}",
                "arrival": f"{last_segment.arrival_time} at {last_segment.arrival_airport}",
                "duration": offer.total_duration,
                "stops": offer.number_of_stops,
                "price": f"{offer.price} {offer.currency}",
                "class": offer.booking_class
            })

        return formatted

    def _format_alternatives_list(
        self,
        alternatives: List[AlternativeDateOffer]
    ) -> List[Dict[str, Any]]:
        """
        Format alternative date offers for LLM.

        Args:
            alternatives: List of alternative date offers

        Returns:
            List of simplified alternative dictionaries
        """
        formatted = []

        for alt in alternatives:
            # Get cheapest flight for this date
            cheapest = min(alt.offers, key=lambda x: x.price)

            formatted.append({
                "date": str(alt.departure_date),
                "savings": f"{abs(alt.price_difference):.2f}",
                "cheapest_price": f"{cheapest.price} {cheapest.currency}",
                "carrier": cheapest.get_carrier_names(),
                "duration": cheapest.total_duration,
                "stops": cheapest.number_of_stops
            })

        return formatted

    def _sort_flights_by_preference(self, offers: List[FlightOffer], user_prompt: str = "") -> List[FlightOffer]:
        """
        Automatically detect sorting preference from user message and sort flights accordingly.
        Defaults to cheapest first if no preference is detected.

        Args:
            offers: List of flight offers to sort
            user_prompt: Original user message to analyze for preferences

        Returns:
            Sorted list of flight offers
        """
        if not offers:
            return offers

        # Detect sorting preference from user's message
        sort_preference = self._detect_sorting_preference(user_prompt)
        
        # Show detected preference to user
        print(f"\n🔍 Sorting flights by: {sort_preference['description']}")
        
        # Sort based on detected preference
        if sort_preference['type'] == 'price_low':
            return sorted(offers, key=lambda x: x.price)
        
        elif sort_preference['type'] == 'price_high':
            return sorted(offers, key=lambda x: x.price, reverse=True)
        
        elif sort_preference['type'] == 'time_early':
            return sorted(offers, key=lambda x: self._extract_departure_time(x))
        
        elif sort_preference['type'] == 'time_late':
            return sorted(offers, key=lambda x: self._extract_departure_time(x), reverse=True)
        
        elif sort_preference['type'] == 'duration_short':
            return sorted(offers, key=lambda x: self._parse_duration_minutes(x.total_duration))
        
        elif sort_preference['type'] == 'duration_long':
            return sorted(offers, key=lambda x: self._parse_duration_minutes(x.total_duration), reverse=True)
        
        elif sort_preference['type'] == 'direct':
            return sorted(offers, key=lambda x: (x.number_of_stops, x.price))
        
        elif sort_preference['type'] == 'airline':
            return sorted(offers, key=lambda x: x.get_carrier_names().lower())
        
        elif sort_preference['type'] == 'best_overall':
            return self._sort_by_overall_score(offers)
        
        # Default: cheapest first
        return sorted(offers, key=lambda x: x.price)

    def _detect_sorting_preference(self, user_prompt: str) -> Dict[str, str]:
        """
        Analyze user's message to detect sorting preferences using keyword matching.

        Args:
            user_prompt: User's original flight request

        Returns:
            Dictionary with preference type and description
        """
        prompt_lower = user_prompt.lower()
        
        # Price-related keywords
        if any(keyword in prompt_lower for keyword in ['cheapest', 'cheap', 'lowest price', 'budget', 'affordable', 'inexpensive']):
            return {'type': 'price_low', 'description': '💰 Cheapest flights first'}
        
        if any(keyword in prompt_lower for keyword in ['expensive', 'premium', 'luxury', 'first class', 'business class']):
            return {'type': 'price_high', 'description': '💰 Premium flights first'}
        
        # Time-related keywords
        if any(keyword in prompt_lower for keyword in ['early morning', 'early', 'first flight', 'morning']):
            return {'type': 'time_early', 'description': '🌅 Early departure times first'}
        
        if any(keyword in prompt_lower for keyword in ['late', 'evening', 'night', 'after', 'pm']):
            return {'type': 'time_late', 'description': '🌙 Later departure times first'}
        
        # Duration-related keywords
        if any(keyword in prompt_lower for keyword in ['fastest', 'quickest', 'shortest', 'quick', 'fast']):
            return {'type': 'duration_short', 'description': '⚡ Shortest flights first'}
        
        # Direct flight keywords
        if any(keyword in prompt_lower for keyword in ['direct', 'non-stop', 'nonstop', 'no stops', 'no connections']):
            return {'type': 'direct', 'description': '✈️ Direct flights first'}
        
        # Airline-specific keywords (if user mentions specific airline)
        airlines = ['american', 'delta', 'united', 'lufthansa', 'emirates', 'qatar', 'singapore', 'british airways']
        if any(airline in prompt_lower for airline in airlines):
            return {'type': 'airline', 'description': '🏢 Sorted by airline name'}
        
        # Default to cheapest
        return {'type': 'price_low', 'description': '💰 Cheapest flights first (default)'}

    def _extract_departure_time(self, offer: FlightOffer) -> str:
        """
        Extract departure time from first segment for sorting.

        Args:
            offer: Flight offer

        Returns:
            Departure time string for comparison
        """
        if offer.segments:
            # Extract time from datetime string (YYYY-MM-DDTHH:MM:SS)
            dept_time = offer.segments[0].departure_time
            if 'T' in dept_time:
                return dept_time.split('T')[1][:5]  # HH:MM
            return dept_time
        return "00:00"

    def _parse_duration_minutes(self, duration_str: str) -> int:
        """
        Parse duration string to minutes for sorting.

        Args:
            duration_str: Duration in format "5h 30m" or "2h 0m"

        Returns:
            Total minutes as integer
        """
        # Extract hours and minutes using regex
        hours_match = re.search(r'(\d+)h', duration_str)
        minutes_match = re.search(r'(\d+)m', duration_str)
        
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        
        return hours * 60 + minutes

    def _sort_by_overall_score(self, offers: List[FlightOffer]) -> List[FlightOffer]:
        """
        Sort flights by overall score considering price, duration, and stops.

        Lower score = better flight
        
        Args:
            offers: List of flight offers

        Returns:
            Sorted list by overall score
        """
        if not offers:
            return offers

        # Calculate min/max values for normalization
        prices = [offer.price for offer in offers]
        durations = [self._parse_duration_minutes(offer.total_duration) for offer in offers]
        
        min_price, max_price = min(prices), max(prices)
        min_duration, max_duration = min(durations), max(durations)
        
        def calculate_score(offer: FlightOffer) -> float:
            # Normalize price (0-100)
            price_score = 0 if max_price == min_price else ((offer.price - min_price) / (max_price - min_price)) * 100
            
            # Normalize duration (0-100)
            duration = self._parse_duration_minutes(offer.total_duration)
            duration_score = 0 if max_duration == min_duration else ((duration - min_duration) / (max_duration - min_duration)) * 100
            
            # Stops penalty (0, 25, 50, 75, 100 for 0, 1, 2, 3, 4+ stops)
            stops_score = min(offer.number_of_stops * 25, 100)
            
            # Weighted total score (lower is better)
            # Price: 50%, Duration: 30%, Stops: 20%
            total_score = (price_score * 0.5) + (duration_score * 0.3) + (stops_score * 0.2)
            
            return total_score

        # Sort by score (ascending - lower is better)
        return sorted(offers, key=calculate_score)

    def get_user_selection(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get and validate user's flight selection with enhanced user experience.

        Args:
            state: Current workflow state

        Returns:
            Updated state with selected flight
        """
        flight_results = FlightSearchResponse.model_validate(state["flight_results"])
        total_options = len(flight_results.original_date_offers)

        if total_options == 0:
            raise ValueError("No flights available for selection")

        while True:
            try:
                print("\n")
                selection = input(f"👆 Enter your choice (1-{total_options}), 'info X' for details, or 'cancel' to exit: ").strip().lower()

                # Handle cancel/exit request
                if selection in ['cancel', 'exit', 'quit', 'q']:
                    print("\n🚪 Booking cancelled by user. Thank you for using AI Ticket Booking!")
                    raise KeyboardInterrupt("User cancelled the booking process")

                # Handle info request (e.g., "info 2" to get details about option 2)
                if selection.startswith('info '):
                    try:
                        info_num = int(selection.split()[1])
                        if 1 <= info_num <= total_options:
                            self._show_flight_details(flight_results.original_date_offers[info_num - 1], info_num)
                            continue
                        else:
                            print(f"❌ Please use 'info X' where X is between 1 and {total_options}")
                            continue
                    except (IndexError, ValueError):
                        print("❌ Invalid format. Use 'info 2' to get details about option 2")
                        continue

                # Handle normal selection
                option_num = int(selection)

                if 1 <= option_num <= total_options:
                    # Valid selection
                    selected_offer = flight_results.original_date_offers[option_num - 1]
                    state["selected_offer"] = selected_offer.model_dump()
                    state["selection_number"] = option_num

                    logger.info(f"User selected option {option_num}: {selected_offer.id}")

                    # Show selection confirmation with details
                    self._show_selection_confirmation(selected_offer, option_num)
                    
                    # Ask for final confirmation
                    confirm = input("\n🤔 Confirm this selection? (y/n/cancel) [y]: ").strip().lower()
                    if confirm in ['', 'y', 'yes']:
                        break
                    elif confirm in ['cancel', 'exit', 'quit']:
                        print("\n🚪 Booking cancelled by user. Thank you for using AI Ticket Booking!")
                        raise KeyboardInterrupt("User cancelled the booking process")
                    else:
                        print("Selection cancelled. Please choose again.")
                        continue

                else:
                    print(f"❌ Please select a number between 1 and {total_options}")
                    continue

            except ValueError:
                print(f"❌ Invalid input. Please enter:")
                print(f"   • A number between 1 and {total_options} (to select flight)")
                print(f"   • 'info X' (for details about option X)")
                print(f"   • 'cancel' (to exit program)")
                continue

        return state

    def _show_flight_details(self, offer: FlightOffer, option_num: int) -> None:
        """
        Show detailed information about a specific flight offer.

        Args:
            offer: Flight offer to show details for
            option_num: Option number for display
        """
        print(f"\n{'='*60}")
        print(f"✈️  DETAILED INFO - OPTION {option_num}")
        print(f"{'='*60}")
        
        print(f"🏢 Carrier: {offer.get_carrier_names()}")
        print(f"💰 Price: {offer.currency} {offer.price:.2f}")
        print(f"🎫 Class: {offer.booking_class}")
        print(f"⏱️  Total Duration: {offer.total_duration}")
        print(f"🔄 Stops: {offer.number_of_stops}")
        print(f"💺 Available Seats: {offer.available_seats or 'N/A'}")
        
        print(f"\n🛫 Flight Segments:")
        for i, segment in enumerate(offer.segments, 1):
            dept_time = segment.departure_time.split('T')[1][:5] if 'T' in segment.departure_time else segment.departure_time
            arr_time = segment.arrival_time.split('T')[1][:5] if 'T' in segment.arrival_time else segment.arrival_time
            
            print(f"   Segment {i}: {segment.carrier_name} {segment.flight_number}")
            print(f"   {segment.departure_airport} ({dept_time}) → {segment.arrival_airport} ({arr_time})")
            print(f"   Duration: {segment.duration}")
            if segment.aircraft:
                print(f"   Aircraft: {segment.aircraft}")
            print()

    def _show_selection_confirmation(self, offer: FlightOffer, option_num: int) -> None:
        """
        Show confirmation details for selected flight.

        Args:
            offer: Selected flight offer
            option_num: Option number selected
        """
        print(f"\n{'='*70}")
        print(f"✅ SELECTION CONFIRMATION - OPTION {option_num}")
        print(f"{'='*70}")
        
        first_segment = offer.segments[0]
        last_segment = offer.segments[-1]
        
        dept_time = first_segment.departure_time.split('T')[1][:5] if 'T' in first_segment.departure_time else first_segment.departure_time
        arr_time = last_segment.arrival_time.split('T')[1][:5] if 'T' in last_segment.arrival_time else last_segment.arrival_time
        
        print(f"🏢 Airline: {offer.get_carrier_names()}")
        print(f"🛫 Route: {first_segment.departure_airport} → {last_segment.arrival_airport}")
        print(f"📅 Departure: {dept_time}")
        print(f"📅 Arrival: {arr_time}")
        print(f"⏱️  Duration: {offer.total_duration}")
        print(f"🔄 Stops: {'Direct flight' if offer.number_of_stops == 0 else f'{offer.number_of_stops} stop(s)'}")
        print(f"🎫 Class: {offer.booking_class}")
        print(f"💰 Total Price: {offer.currency} {offer.price:.2f}")
        print(f"{'='*70}")


# Example usage for testing
if __name__ == "__main__":
    # Mock state for testing
    from datetime import date

    mock_state = {
        "parsed_request": {
            "origin_city": "New York",
            "origin_code": "JFK",
            "destination_city": "Los Angeles",
            "destination_code": "LAX",
            "departure_date": "2025-11-15"
        },
        "flight_results": {
            "original_date_offers": [],
            "alternative_offers": []
        }
    }

    agent = FlightPresentationAgent()
    # result = agent.execute(mock_state)
    print("Flight Presentation Agent ready for testing")
