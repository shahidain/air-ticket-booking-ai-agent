# AI Agents Documentation 🤖

Complete guide for AI agents and LLMs to understand and work with this multi-agent flight booking system.

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Agent Specifications](#agent-specifications)
4. [Data Flow](#data-flow)
5. [API Integration](#api-integration)
6. [Tools & Functions](#tools--functions)
7. [State Management](#state-management)
8. [Error Handling](#error-handling)
9. [Extension Guide](#extension-guide)

---

## System Overview

### Purpose
An intelligent multi-agent system that automates flight ticket booking using natural language processing, LangGraph orchestration, and real-time API integrations.

### Tech Stack
- **Framework**: LangGraph (StateGraph) for agent orchestration
- **LLM**: OpenAI GPT-4o-mini for natural language understanding
- **Flight API**: Amadeus Travel API v12.0.0
- **Currency API**: Open Exchange Rates API
- **Validation**: Pydantic v2.0+ for type safety
- **Language**: Python 3.11+

### Key Design Principles
1. **Separation of Concerns**: Each agent handles ONE specific task
2. **Tool-Based Architecture**: Agents use tools via OpenAI function calling
3. **State Management**: LangGraph manages shared state across agents
4. **Human-in-the-Loop**: User confirmation at critical decision points
5. **Fail-Safe**: Multiple exit points and graceful error handling

---

## Architecture

### High-Level Flow
```
User Input (Natural Language)
    ↓
[LangGraph Workflow Orchestrator]
    ↓
Agent 1: Flight Search (with Tools) → Parse request, search flights
    ↓
Agent 2: Presentation → Format, sort, display with currency conversion
    ↓
[User Selection] → Human-in-the-loop decision point
    ↓
Agent 3: Booking → Collect passenger info, validate ID, book
    ↓
Agent 4: Ticket Generation → Calculate GST, format ticket
    ↓
Agent 5: Notification → Deliver confirmation
    ↓
Booking Complete ✅
```

### Component Structure
```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                        │
│                 (Natural Language)                      │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│            LangGraph Workflow Engine                    │
│  • State Management  • Agent Coordination               │
│  • Checkpointing     • Error Recovery                   │
└──────────────────────┬──────────────────────────────────┘
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
┌───────────────┐            ┌───────────────┐
│   AI Agents   │            │     Tools     │
│  (5 Agents)   │←──────────→│  (2 Tools)    │
└───────┬───────┘            └───────────────┘
        ↓
┌───────────────────────────────────────────┐
│         External Services                 │
│  • Amadeus API (Flights, Airports)        │
│  • OpenAI API (LLM)                       │
│  • Exchange Rate API (Currency)           │
└───────────────────────────────────────────┘
```

---

## Agent Specifications

### Agent 1: Flight Search Agent
**File**: `agents/flight_search_agent.py`

**Responsibility**: Parse natural language requests and search for flights using Amadeus API.

**Input State**:
- `user_prompt`: String (e.g., "Find cheapest flight from Mumbai to Delhi tomorrow")

**Output State**:
- `parsed_request`: Dictionary with origin, destination, date, adults
- `flight_results`: FlightSearchResponse with offers and alternatives

**Tools Used**:
- `get_primary_airport(city_name)`: Resolve city → IATA code via Amadeus API
- `lookup_airports_by_city(city_name)`: Get all airports in a city
- `lookup_airport_by_code(code)`: Get airport details by IATA code

**Process Flow**:
```python
1. Use OpenAI function calling to parse user request
   - Extract: origin city, destination city, date, time, adults
   - Dynamically call airport lookup tools to resolve IATA codes

2. Search flights via Amadeus API
   - Use parsed IATA codes (e.g., BOM → DEL)
   - Get available flights for requested date

3. Find cheaper alternatives
   - Search ±1 day from requested date
   - Compare prices and identify savings

4. Return structured response
   - Original date offers (up to 10 flights)
   - Alternative date offers with price differences
```

**Example Tool Call**:
```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "function": {
        "name": "get_primary_airport",
        "arguments": "{\"city_name\": \"Mumbai\"}"
      }
    }
  ]
}
// Returns: "BOM"
```

**Key Features**:
- Smart date parsing (tomorrow, next Monday, 2024-11-20)
- Flexible time preferences (morning, afternoon, evening)
- Multi-iteration tool calling until all info extracted
- Comprehensive error handling for API failures

---

### Agent 2: Flight Presentation Agent
**File**: `agents/presentation_agent.py`

**Responsibility**: Convert flight data to user-friendly format with currency conversion, sorting, and professional display.

**Input State**:
- `flight_results`: FlightSearchResponse with EUR/USD prices
- `parsed_request`: Original request data
- `user_prompt`: For preference detection

**Output State**:
- `presentation`: Formatted string for display
- `flight_results`: Updated with INR prices (saved back to state)

**Process Flow**:
```python
1. Currency Conversion
   - Check if ENABLE_CURRENCY_CONVERSION = true
   - Convert all prices to LOCAL_CURRENCY (e.g., EUR → INR)
   - Update state with converted prices

2. Intelligent Sorting
   - Detect user preferences from message
   - Keywords: "cheapest", "fastest", "direct", "early morning"
   - Sort accordingly (price/duration/time/stops)

3. Format Display
   - Create ASCII table with box-drawing characters
   - Show: Carrier, Departure, Arrival, Duration, Stops, Price*
   - Add asterisk (*) with GST notice
   - Display alternative dates if cheaper

4. User Selection
   - Prompt for flight number or commands
   - Support: 'info X' (details), 'cancel' (exit)
   - Validate and confirm selection
```

**Sorting Keywords**:
| User Says | Sort By | Example |
|-----------|---------|---------|
| "cheapest", "cheap", "budget" | Price (Low→High) | ₹25,450 → ₹31,200 |
| "fastest", "quickest", "shortest" | Duration (Short→Long) | 2h 30m → 5h 15m |
| "direct", "non-stop" | Stops (0 first) | Direct → 1 stop → 2 stops |
| "early morning", "first flight" | Time (Early→Late) | 06:00 → 18:00 |

**Display Format**:
```
💱 Prices shown in: ₹ INR
* 18% GST will be added to the fare price at checkout

┌─────────────────────────────────────────────────────┐
│ # │ Carrier     │ Departure │ Arrival │ Price       │
├─────────────────────────────────────────────────────┤
│ 1 │ Air India   │ BOM 06:00 │ DEL 08:30│ INR 5,450*│
│ 2 │ IndiGo      │ BOM 08:15 │ DEL 10:45│ INR 4,200*│
└─────────────────────────────────────────────────────┘
```

**Key Methods**:
- `_convert_currencies()`: EUR/USD → INR conversion
- `_sort_flights_by_preference()`: Auto-detect and sort
- `_format_flight_presentation()`: ASCII table generation
- `get_user_selection()`: Handle user input with safe exit

---

### Agent 3: Booking Agent
**File**: `agents/booking_agent.py`

**Responsibility**: Collect passenger information with validation and initiate booking.

**Input State**:
- `selected_offer`: FlightOffer chosen by user
- `parsed_request`: For number of passengers

**Output State**:
- `booking_confirmation`: BookingConfirmation object
- `passengers`: List of PassengerInfo

**Process Flow**:
```python
1. Collect Passenger Info (for each passenger)
   - First Name, Last Name (with 'cancel' option)
   - Gender (M/F)
   - Email, Phone

2. Government ID Collection
   - Prompt: AADHAAR (default), PASSPORT, DRIVING_LICENSE
   - AADHAAR validation: 12 digits in format 0000-0000-0000
   - Auto-format: "123456789012" → "1234-5678-9012"

3. Initiate Booking
   - Call Amadeus API book_flight()
   - Demo mode: Generate PNR (e.g., "XYZ123")
   - Production: Real booking with payment

4. Return Confirmation
   - BookingConfirmation with PNR
   - Status: CONFIRMED/PENDING
   - Flight details and passenger list
```

**AADHAAR Validation**:
```python
def _get_aadhaar_number(self) -> str:
    while True:
        aadhaar = input("AADHAAR Number (12 digits): ")
        if not aadhaar:  # Demo mode
            return "1234-5678-9012"

        digits = aadhaar.replace("-", "").replace(" ", "")
        if len(digits) == 12 and digits.isdigit():
            return f"{digits[:4]}-{digits[4:8]}-{digits[8:]}"
        else:
            print("❌ Invalid! Must be 12 digits")
```

**Safe Exit Points**:
- First Name input: Type 'cancel' to exit
- ID Number input: Type 'cancel' to exit
- Each input field validates and handles exit

---

### Agent 4: Ticket Generation Agent
**File**: `agents/ticket_generation_agent.py`

**Responsibility**: Generate professional ticket document with GST calculation and formatting.

**Input State**:
- `booking_confirmation`: BookingConfirmation object

**Output State**:
- `formatted_ticket`: String (professional ticket)

**Process Flow**:
```python
1. Currency Conversion (if needed)
   - Convert booking price to LOCAL_CURRENCY
   - Example: USD 365.50 → INR 30,500

2. GST Calculation
   - base_fare = converted price
   - gst_amount = base_fare * (GST_RATE / 100)
   - total_with_gst = base_fare + gst_amount

3. Prepare Ticket Data
   - Booking reference (PNR)
   - Passenger info with Government ID
   - Flight segments with times
   - Price breakdown (Base + GST = Total)

4. LLM Formatting
   - Use OpenAI to create professional ticket
   - Instruction: "Create airline ticket with price breakdown"
   - Return formatted text with borders and emojis
```

**Price Breakdown Structure**:
```python
ticket_data = {
    "base_fare": "₹30,500.00 INR",
    "gst_rate": "18%",
    "gst_amount": "₹5,490.00 INR",
    "total_price": "₹35,990.00 INR",
    # ... other details
}
```

**Example Output**:
```
╔═══════════════════════════════════════════╗
║     ✈️ E-TICKET / BOARDING PASS          ║
╚═══════════════════════════════════════════╝

📋 Booking Reference: XYZ789ABC
✅ Status: CONFIRMED

👤 Passenger Information:
   Name: John Doe
   ID: AADHAAR 1234-5678-9012
   Email: john.doe@example.com

✈️ Flight Details:
   AI 2658: BOM → DEL
   Departure: 2024-11-20 06:00
   Arrival: 2024-11-20 08:30

💰 Price Breakdown:
   Base Fare:    ₹30,500.00 INR
   GST (18%):    ₹5,490.00 INR
   ─────────────────────────────
   Total Amount: ₹35,990.00 INR

⚠️ Important Information:
   • Check-in opens 24 hours before
   • Arrive 2-3 hours before departure
   • Valid ID required at airport
```

---

### Agent 5: Notification Agent
**File**: `agents/notification_agent.py`

**Responsibility**: Deliver final confirmation to user.

**Input State**:
- `formatted_ticket`: Professional ticket string
- `booking_confirmation`: For metadata

**Output State**:
- No state changes (final agent)

**Process Flow**:
```python
1. Display Ticket
   - Print formatted_ticket to console

2. Simulate Notifications (Demo)
   - Console: "📧 Email sent to user@example.com"
   - Console: "📱 SMS sent to +91-1234567890"

3. Production (TODO)
   - Send actual email via SendGrid/AWS SES
   - Send SMS via Twilio
   - Store confirmation in database
```

---

## Data Flow

### State Object Structure
The LangGraph state is a dictionary that flows through all agents:

```python
{
    # From User
    "user_prompt": "Find cheapest flight from Mumbai to Delhi tomorrow",

    # From Agent 1
    "parsed_request": {
        "origin_city": "Mumbai",
        "origin_code": "BOM",
        "destination_city": "Delhi",
        "destination_code": "DEL",
        "departure_date": "2024-11-20",
        "adults": 1
    },
    "flight_results": {
        "original_date_offers": [FlightOffer, ...],
        "alternative_offers": [AlternativeDateOffer, ...]
    },

    # From Agent 2
    "presentation": "Formatted flight table...",
    "selected_offer": FlightOffer,  # User's choice
    "selection_number": 2,

    # From Agent 3
    "booking_confirmation": BookingConfirmation,
    "passengers": [PassengerInfo, ...],

    # From Agent 4
    "formatted_ticket": "Professional ticket text...",

    # Error Handling
    "error": None  # or error message string
}
```

### Pydantic Models

**FlightOffer** (`models/flight_models.py`):
```python
class FlightOffer(BaseModel):
    id: str
    price: float
    currency: str  # EUR, USD, INR
    segments: List[FlightSegment]
    total_duration: str  # "2h 30m"
    number_of_stops: int
    booking_class: str  # ECONOMY, BUSINESS
    available_seats: Optional[int]

    # Helper methods
    def calculate_gst(self, rate: float) -> float
    def get_total_with_gst(self, rate: float) -> float
    def convert_currency(self, target: str) -> FlightOffer
```

**PassengerInfo**:
```python
class PassengerInfo(BaseModel):
    first_name: str
    last_name: str
    gender: str  # M or F
    email: str
    phone: str
    id_type: str  # AADHAAR, PASSPORT, DRIVING_LICENSE
    id_number: str  # Validated format
    nationality: Optional[str] = None
```

---

## API Integration

### Amadeus API

**Endpoints Used**:
1. **Flight Search**: `POST /v2/shopping/flight-offers`
2. **Location Search**: `GET /v1/reference-data/locations?keyword={city}&subType=AIRPORT`
3. **Booking** (Demo): Simulated with mock data

**Authentication**:
```python
# In api/amadeus_client.py
from amadeus import Client

client = Client(
    client_id=AMADEUS_API_KEY,
    client_secret=AMADEUS_API_SECRET,
    hostname='test'  # or 'production'
)
```

**Flight Search Example**:
```python
response = client.shopping.flight_offers_search.get(
    originLocationCode='BOM',
    destinationLocationCode='DEL',
    departureDate='2024-11-20',
    adults=1,
    max=10
)
```

**Location Search Example**:
```python
response = client.reference_data.locations.get(
    keyword='Mumbai',
    subType='AIRPORT'
)
# Returns: [{iataCode: 'BOM', name: 'Chhatrapati Shivaji', ...}, ...]
```

### OpenAI API

**Function Calling for Tools**:
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a flight booking assistant"},
        {"role": "user", "content": "Book flight from Mumbai to Delhi"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_primary_airport",
                "description": "Get primary airport for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_name": {"type": "string"}
                    }
                }
            }
        }
    ],
    tool_choice="auto"
)
```

**Ticket Formatting**:
```python
formatted = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Format airline ticket"},
        {"role": "user", "content": json.dumps(ticket_data)}
    ],
    temperature=0.5
)
```

### Exchange Rate API

**Endpoint**: `https://open.er-api.com/v6/latest/{BASE_CURRENCY}`

**Response**:
```json
{
  "result": "success",
  "base_code": "USD",
  "rates": {
    "EUR": 0.92,
    "GBP": 0.79,
    "INR": 83.12,
    "AED": 3.67,
    ...
  }
}
```

---

## Tools & Functions

### Airport Lookup Tool

**File**: `tools/airport_lookup_tool.py`

**Amadeus Integration**:
```python
def _fetch_airport_from_amadeus(cls, city_or_code: str) -> List[AirportInfo]:
    amadeus = AmadeusClient()
    response = amadeus.client.reference_data.locations.get(
        keyword=city_or_code,
        subType='AIRPORT'
    )

    airports = []
    for location in response.data:
        airport = AirportInfo(
            iata_code=location['iataCode'],
            city=location['address']['cityName'],
            country=location['address']['countryName'],
            airport_name=location['name'],
            is_major='international' in location['name'].lower()
        )
        airports.append(airport)

    return airports
```

**Functions Exposed to Agents**:
```python
AIRPORT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_primary_airport",
            "description": "Get primary airport IATA code for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {"type": "string"}
                },
                "required": ["city_name"]
            }
        }
    },
    # ... more functions
]
```

**Data Strategy**:
- Real-time API calls only - no caching or fallback
- Direct Amadeus API integration for all airport lookups
- Raises exceptions if API is unavailable

### Currency Converter Tool

**File**: `tools/currency_converter_tool.py`

**Core Function**:
```python
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert amount between currencies.

    Examples:
        convert_currency(100, "USD", "INR")  # → 8312.0
        convert_currency(305.50, "EUR", "INR")  # → 31,455.65
    """
    if from_currency == to_currency:
        return amount

    rate = CurrencyConverterTool.get_exchange_rate(from_currency, to_currency)
    return round(amount * rate, 2)
```

**Symbol Mapping**:
```python
SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥",
    "AED": "د.إ",
    # ... 15+ more
}
```

---

## State Management

### LangGraph StateGraph

**Workflow Definition** (`workflows/booking_workflow.py`):
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(BookingState)

# Add nodes (agents)
workflow.add_node("search", search_agent.execute)
workflow.add_node("present", presentation_agent.execute)
workflow.add_node("get_selection", presentation_agent.get_user_selection)
workflow.add_node("book", booking_agent.execute)
workflow.add_node("generate_ticket", ticket_agent.execute)
workflow.add_node("notify", notification_agent.execute)

# Define edges (flow)
workflow.set_entry_point("search")
workflow.add_edge("search", "present")
workflow.add_edge("present", "get_selection")
workflow.add_edge("get_selection", "book")
workflow.add_edge("book", "generate_ticket")
workflow.add_edge("generate_ticket", "notify")
workflow.add_edge("notify", END)

app = workflow.compile()
```

**Execution**:
```python
async def run(self, user_prompt: str):
    initial_state = {"user_prompt": user_prompt}
    result = await app.ainvoke(initial_state)
    return result
```

### State Updates

Each agent receives state, modifies it, and returns updated state:
```python
def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # Read from state
    user_prompt = state["user_prompt"]

    # Process
    flight_results = self.search_flights(user_prompt)

    # Update state
    state["flight_results"] = flight_results
    state["parsed_request"] = parsed_request

    return state  # LangGraph automatically merges
```

---

## Error Handling

### Levels of Error Handling

1. **API Errors**:
```python
try:
    response = amadeus.client.shopping.flight_offers_search.get(...)
except ResponseError as e:
    logger.error(f"Amadeus API error: {e}")
    raise  # Re-raise exception, no fallback
```

2. **Validation Errors**:
```python
try:
    passenger = PassengerInfo.model_validate(data)
except ValidationError as e:
    logger.error(f"Invalid passenger data: {e}")
    # Re-prompt user
```

3. **User Cancellation**:
```python
if user_input.lower() in ['cancel', 'exit', 'quit']:
    raise KeyboardInterrupt("User cancelled")
```

4. **Workflow Errors**:
```python
try:
    result = await workflow.run(user_prompt)
except Exception as e:
    logger.error(f"Workflow error: {e}")
    state["error"] = str(e)
    # Graceful shutdown
```

### Logging

**Configuration** (`utils/logger.py`):
```python
import logging
import colorlog

def setup_logger(name: str) -> logging.Logger:
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    return logger
```

---

## Extension Guide

### Adding a New Agent

1. **Create Agent File**: `agents/my_new_agent.py`
```python
class MyNewAgent:
    def __init__(self):
        self.client = SomeClient()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Your logic
        state["new_data"] = result
        return state
```

2. **Update Workflow**: `workflows/booking_workflow.py`
```python
workflow.add_node("my_new_step", my_new_agent.execute)
workflow.add_edge("previous_step", "my_new_step")
workflow.add_edge("my_new_step", "next_step")
```

3. **Update State Type**:
```python
class BookingState(TypedDict):
    # ... existing fields
    new_data: Optional[YourType]
```

### Adding a New Tool

1. **Create Tool File**: `tools/my_tool.py`
```python
def my_tool_function(param: str) -> str:
    # Your logic
    return result

MY_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "my_tool_function",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        }
    }
}

TOOL_FUNCTIONS = {
    "my_tool_function": my_tool_function
}
```

2. **Integrate with Agent**:
```python
from tools.my_tool import MY_TOOL_DEFINITION, TOOL_FUNCTIONS

class MyAgent:
    def __init__(self):
        self.tools = [MY_TOOL_DEFINITION]
        self.tool_functions = TOOL_FUNCTIONS

    def execute(self, state):
        response = openai.chat.completions.create(
            tools=self.tools,
            ...
        )

        for tool_call in response.tool_calls:
            result = self.tool_functions[tool_call.function.name](
                **tool_call.arguments
            )
```

### Adding New Configuration

1. **Environment Variable**: `.env`
```env
MY_NEW_CONFIG=value
```

2. **Config Class**: `config.py`
```python
class Settings(BaseSettings):
    my_new_config: str = "default_value"
```

3. **Usage**:
```python
from config import settings
print(settings.my_new_config)
```

---

## Quick Reference

### File Locations
- **Agents**: `agents/*.py`
- **Tools**: `tools/*.py`
- **Models**: `models/flight_models.py`
- **Workflow**: `workflows/booking_workflow.py`
- **Config**: `config.py`, `.env`
- **Main**: `main.py`

### Key Commands
```bash
# Run application
python main.py

# Test tools
python -c "from tools.airport_lookup_tool import *; print(get_primary_airport('Mumbai'))"

# Test currency
python -c "from tools.currency_converter_tool import *; print(convert_currency(100, 'USD', 'INR'))"
```

### Environment Variables
| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI authentication | `sk-proj-...` |
| `AMADEUS_API_KEY` | Amadeus client ID | `abc123...` |
| `AMADEUS_API_SECRET` | Amadeus secret | `xyz789...` |
| `LOCAL_CURRENCY` | User's currency | `INR`, `USD` |
| `GST_RATE` | Tax percentage | `18.0` |
| `ENABLE_CURRENCY_CONVERSION` | Auto-convert? | `true`/`false` |

---

## Debugging Tips

### Enable Debug Logging
```env
LOG_LEVEL=DEBUG
```

### Test Individual Agents
```python
# In Python REPL or script
from agents.flight_search_agent import FlightSearchAgent

agent = FlightSearchAgent()
state = {"user_prompt": "Mumbai to Delhi tomorrow"}
result = agent.execute(state)
print(result)
```

### Inspect State at Each Step
```python
# In workflow
def debug_node(state):
    import json
    print(json.dumps(state, indent=2, default=str))
    return state

workflow.add_node("debug", debug_node)
workflow.add_edge("search", "debug")
```

---

**For detailed code examples, see the source files. For issues, check logs with colored output for easy debugging.**

**Last Updated**: 2025-10-15
**Version**: 1.0
**Maintained by**: AI-TICKET-BOOKING Project
