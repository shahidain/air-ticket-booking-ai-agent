# AI Ticket Booking System 🤖✈️

A multi-agent AI system for automated flight ticket booking using **LangGraph**, **OpenAI**, and **Amadeus API**.

## 🌟 Features

- **Natural Language Processing**: Book flights using plain English
- **AI Agent Tools**: Agents use tools like airport lookup for intelligent decision-making
- **OpenAI Function Calling**: Agents dynamically call tools to resolve airport codes
- **Intelligent Flight Search**: Automatically finds cheaper alternatives ±1 day
- **Currency Conversion**: Automatic conversion to your local currency with real-time exchange rates
- **Smart Flight Sorting**: Automatically detects preferences from your message (cheapest, direct, fastest, etc.)
- **5 Specialized AI Agents**: Each handling a specific task
- **Professional Ticket Generation**: LLM-powered ticket formatting
- **LangGraph Orchestration**: State management and agent coordination
- **Human-in-the-Loop**: User selection and confirmation at key steps
- **Cancel Anytime**: Exit the program gracefully at any step

## 📋 System Architecture

```
User Input
    ↓
┌───────────────────────────────────────────────────────────┐
│  LangGraph Workflow Orchestrator                          │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│  Agent 1: Flight Search Agent (with Tools)                │
│  - Parses natural language request using OpenAI           │
│  - Uses airport lookup tool to resolve city → IATA codes  │
│  - Extracts origin, destination, date, time               │
│  - Searches flights via Amadeus API                       │
│  - Finds cheaper alternatives (±1 day)                    │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│  Agent 2: Flight Presentation Agent                       │
│  - Formats flight offers using LLM                        │
│  - Shows carrier names, times, duration, prices           │
│  - Presents alternatives with savings                     │
│  - Asks user to select option                             │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│  Agent 3: Booking Agent                                   │
│  - Collects passenger information                         │
│  - Initiates booking via Amadeus API                      │
│  - Returns booking confirmation                           │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│  Agent 4: Ticket Generation Agent                         │
│  - Formats booking confirmation into ticket               │
│  - Creates professional ticket document                   │
│  - Includes PNR, flight details, passenger info           │
└───────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────┐
│  Agent 5: Notification Agent                              │
│  - Delivers formatted ticket to user                      │
│  - Shows booking reference and next steps                 │
│  - (Production: sends email/SMS)                          │
└───────────────────────────────────────────────────────────┘
    ↓
Booking Complete ✅
```

## 📁 Project Structure

```
AI-TICKET-BOOKING/
├── main.py                      # Main entry point - Run this to start the app
├── config.py                    # Configuration and environment variables
├── requirements.txt             # Python dependencies
├── README.md                    # Documentation (this file)
├── .env.example                 # Environment variables template
├── .env                         # Your API keys (create from .env.example)
└── .gitignore                   # Git ignore rules
│
├── agents/                      # AI Agents (5 separate agents)
│   ├── __init__.py
│   ├── flight_search_agent.py   # Agent 1: Search flights with tools
│   ├── presentation_agent.py    # Agent 2: Format and display options
│   ├── booking_agent.py         # Agent 3: Book tickets
│   ├── ticket_generation_agent.py   # Agent 4: Generate ticket document
│   └── notification_agent.py    # Agent 5: Send confirmation
│
├── api/                         # External API Clients
│   ├── __init__.py
│   ├── amadeus_client.py        # Amadeus flight API integration
│   └── openai_client.py         # OpenAI LLM wrapper
│
├── tools/                       # Agent Tools
│   ├── __init__.py
│   └── airport_lookup_tool.py   # Airport code lookup (70+ airports)
│
├── models/                      # Data Models
│   ├── __init__.py
│   └── flight_models.py         # Pydantic models for validation
│
├── workflows/                   # LangGraph Orchestration
│   ├── __init__.py
│   └── booking_workflow.py      # Main workflow connecting all agents
│
└── utils/                       # Utilities
    ├── __init__.py
    └── logger.py                # Colored logging setup
```

### 📊 File Count Summary

- **Total application files**: 18 Python files
- **Agents**: 5 files
- **API clients**: 2 files
- **Tools**: 1 file
- **Models**: 1 file
- **Workflows**: 1 file
- **Configuration**: 2 files (config.py, main.py)
- **Utilities**: 1 file

### 🏗️ Clean Architecture

✅ **Production ready** - Clean, organized structure  
✅ **Easy to maintain** - Each component isolated  
✅ **Well documented** - Clear code comments  
✅ **Type safety** - Pydantic models throughout  
✅ **Modular design** - Easy to extend and maintain

## 🚀 Setup Instructions

### 1. Clone and Navigate

```bash
cd AI-TICKET-BOOKING
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# OpenAI API (required)
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini

# Amadeus API (required)
AMADEUS_API_KEY=your-amadeus-key-here
AMADEUS_API_SECRET=your-amadeus-secret-here
AMADEUS_HOSTNAME=test  # Use 'test' for testing, 'production' for live

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development

# Currency Configuration
LOCAL_CURRENCY=USD  # Your preferred currency (USD, EUR, GBP, INR, etc.)
ENABLE_CURRENCY_CONVERSION=true  # Enable automatic currency conversion
```

#### Getting API Keys:

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Copy to `.env`

**Amadeus:**
1. Go to https://developers.amadeus.com/
2. Create free account
3. Create new app to get API key and secret
4. Start with `test` environment (free)

### 5. Run the Application

```bash
# Main application
python main.py

# Example usage script (recommended for first run)
python example_usage.py
```

## 💡 Usage Examples

### Example 1: Basic Flight Search

```
User: "Book a flight from New York to Los Angeles on November 20th"
```

**What happens:**
1. Agent 1 searches flights JFK→LAX
2. Agent 2 shows options with prices
3. Finds cheaper flights on Nov 19th and 21st
4. User selects preferred option
5. Agent 3 collects passenger info and books
6. Agent 4 generates ticket
7. Agent 5 delivers confirmation

### Example 2: With Time Preference

```
User: "I need to fly from London to Paris tomorrow at 3 PM"
```

### Example 3: Multiple Passengers

```
User: "Book 2 business class tickets from Dubai to New York on December 15th"
```

## 🏗️ How Each Component Works

### Agents (`agents/`)

Each agent is isolated in its own file with a single responsibility:

- **`FlightSearchAgent`**:
  - Uses OpenAI function calling with tools
  - Dynamically calls airport lookup tool
  - Parses natural language requests
  - Searches flights via Amadeus API

- **`PresentationAgent`**: Formats data using LLM for user-friendly display
- **`BookingAgent`**: Handles passenger data collection and booking
- **`TicketGenerationAgent`**: Uses LLM to create professional ticket format
- **`NotificationAgent`**: Final delivery (console in demo, email/SMS in production)

### Tools (`tools/`)

Reusable tools that agents can call using OpenAI function calling:

- **`AirportLookupTool`**:
  - Database of 70+ major airports worldwide
  - `lookup_airport_by_code(iata_code)`: Get airport info by IATA code
  - `lookup_airports_by_city(city_name)`: Find all airports in a city
  - `get_primary_airport(city_name)`: Get main airport for a city
  - Used by Flight Search Agent to resolve city names → IATA codes

**Example Tool Usage:**
```python
# When user says "New York", agent calls:
get_primary_airport("New York")  # Returns: "JFK"

# When user says "London", agent calls:
get_primary_airport("London")  # Returns: "LHR"
```

### API Clients (`api/`)

Separated for clean code management:

- **`AmadeusClient`**:
  - Flight search with flexible dates
  - Parsing Amadeus responses
  - Booking operations (demo mode)

- **`OpenAIClient`**:
  - Structured output generation (JSON mode)
  - Chat completions
  - Response formatting

### Workflow (`workflows/`)

**`BookingWorkflow`** uses LangGraph to:
- Define agent execution order
- Manage state between agents
- Handle human-in-the-loop interactions
- Provide checkpointing and error recovery

## 🔧 Configuration

Edit `config.py` or use environment variables:

```python
# OpenAI Model Selection
OPENAI_MODEL=gpt-4o-mini  # Fast and cost-effective
# or
OPENAI_MODEL=gpt-4o       # More powerful

# Amadeus Environment
AMADEUS_HOSTNAME=test      # Free tier, test data
# or
AMADEUS_HOSTNAME=production  # Real bookings (charges apply)

# Currency Configuration
LOCAL_CURRENCY=USD         # Your preferred currency (USD, EUR, GBP, INR, AED, etc.)
ENABLE_CURRENCY_CONVERSION=true  # Enable automatic currency conversion

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### 💱 Currency Conversion

The system automatically converts flight prices to your preferred local currency:

**Supported Currencies:**
- 🇺🇸 USD - US Dollar
- 🇪🇺 EUR - Euro
- 🇬🇧 GBP - British Pound
- 🇮🇳 INR - Indian Rupee
- 🇦🇪 AED - UAE Dirham
- 🇨🇦 CAD - Canadian Dollar
- 🇦🇺 AUD - Australian Dollar
- 🇯🇵 JPY - Japanese Yen
- 🇨🇳 CNY - Chinese Yuan
- 🇸🇬 SGD - Singapore Dollar
- And 10+ more currencies

**Features:**
- Real-time exchange rates from API
- Fallback rates when offline
- Automatic conversion of all prices
- Currency symbols displayed correctly
- Original currency preserved in data

**How it works:**
1. Set `LOCAL_CURRENCY` in `.env` file (e.g., `LOCAL_CURRENCY=INR`)
2. System fetches latest exchange rates
3. All flight prices automatically converted
4. Prices displayed with proper currency symbols (₹, $, €, £, etc.)

**Example:**
```
Flight found: $500 USD → Displayed as: ₹41,560 INR
```

## 📊 Data Models

All data is validated using **Pydantic** models in `models/flight_models.py`:

- `FlightSegment`: Individual flight leg
- `FlightOffer`: Complete offer with pricing
- `FlightSearchRequest`: Search parameters
- `FlightSearchResponse`: Results with alternatives
- `PassengerInfo`: Passenger details
- `BookingConfirmation`: Final booking details

## 🛡️ Error Handling

The system includes:
- API error handling (rate limits, timeouts)
- Input validation (Pydantic models)
- Graceful fallbacks
- Comprehensive logging

## 🚦 Development Status

### ✅ Implemented
- [x] All 5 agents
- [x] OpenAI function calling with tools
- [x] Airport lookup tool (70+ airports)
- [x] LangGraph workflow orchestration
- [x] Amadeus API integration
- [x] OpenAI LLM integration
- [x] Natural language parsing
- [x] Alternative date search
- [x] Passenger data collection
- [x] Ticket generation

### 🚧 Demo Limitations
- ⚠️ Booking API in demo mode (no real bookings)
- ⚠️ Payment processing not implemented
- ⚠️ Email/SMS notifications simulated

### 🔮 Future Enhancements
- [ ] Real payment integration (Stripe, PayPal)
- [ ] Email notifications (SendGrid, AWS SES)
- [ ] SMS notifications (Twilio)
- [ ] Database persistence (PostgreSQL, MongoDB)
- [ ] Web interface (FastAPI, React)
- [ ] Round-trip flights
- [ ] Multi-city routes
- [ ] Seat selection
- [ ] Calendar integration

## 🧪 Testing

### Test Tools

Test the airport lookup tool:

```bash
python test_tools.py
```

This demonstrates:
- Looking up airports by IATA code
- Finding airports by city name
- Getting primary airport for a city
- How the agent uses these tools

### Test Individual Agents

Each agent file can be run standalone:

```bash
python agents/flight_search_agent.py
python agents/presentation_agent.py
# etc.
```

### Test Full Workflow

```bash
python example_usage.py
```

## 📝 Notes

### Amadeus Test Environment

- Uses test data (not real flights)
- Free tier available
- Limited to test bookings
- Switch to `production` for real bookings

### OpenAI Costs

- Model `gpt-4o-mini`: ~$0.15 per 1M input tokens
- Typical booking flow: ~10-20K tokens
- Estimated cost per booking: $0.002 - $0.005

### Rate Limits

- OpenAI: 500 requests/minute (tier 1)
- Amadeus Test: 10 requests/second
- Implement caching for production

## 🤝 Contributing

This is a demonstration project. To extend:

1. Fork the repository
2. Create feature branch
3. Add your enhancements
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - Feel free to use for learning and development

## 🐛 Troubleshooting

### "Config file not found"
→ Create `.env` file from `.env.example`

### "Amadeus API error"
→ Check API keys in `.env`
→ Verify account status on Amadeus portal

### "OpenAI rate limit"
→ Wait a few minutes
→ Reduce number of requests

### "No flights found"
→ Check IATA codes are valid
→ Try different dates
→ Verify Amadeus API is working

## 📞 Support

For issues or questions:
1. Check this README first
2. Review agent logs (colored console output)
3. Test individual agents
4. Check API credentials

## 🎓 Learning Resources

- **LangGraph**: https://python.langchain.com/docs/langgraph
- **Amadeus API**: https://developers.amadeus.com/self-service
- **OpenAI API**: https://platform.openai.com/docs
- **Pydantic**: https://docs.pydantic.dev/

---

**Built with ❤️ using LangGraph, OpenAI, and Amadeus API**
