"""
Agent 1: Flight Search Agent

This agent is the first in the booking workflow. It:
1. Parses user's natural language request using LLM with tool support
2. Uses airport lookup tool to resolve city names to IATA codes
3. Extracts flight search parameters (origin, destination, date, time)
4. Searches for flights using Amadeus API
5. Finds cheaper alternatives on nearby dates (±1 day)
6. Returns structured flight data to the next agent
"""

from typing import Dict, Any
from datetime import datetime, date, time
from pydantic import BaseModel, Field
import json
from openai import OpenAI

from api.openai_client import OpenAIClient
from api.amadeus_client import AmadeusClient
from models.flight_models import FlightSearchRequest, FlightSearchResponse
from tools.airport_lookup_tool import AIRPORT_TOOLS, TOOL_FUNCTIONS
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)


class ParsedFlightRequest(BaseModel):
    """Structured output from LLM parsing user request."""

    origin_city: str = Field(description="Origin city name")
    origin_code: str = Field(description="Origin airport IATA code (3 letters)")
    destination_city: str = Field(description="Destination city name")
    destination_code: str = Field(description="Destination airport IATA code (3 letters)")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")
    departure_time: str | None = Field(
        default=None,
        description="Preferred departure time in HH:MM format (24-hour), null if not specified"
    )
    adults: int = Field(default=1, description="Number of adult passengers")
    travel_class: str = Field(
        default="ECONOMY",
        description="Travel class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, or FIRST"
    )


class FlightSearchAgent:
    """
    Agent 1: Parses user requests and searches for flights.

    This is the entry point of the booking workflow.
    """

    def __init__(self):
        """Initialize the agent with API clients and tools."""
        self.openai_client = OpenAIClient()
        self.amadeus_client = AmadeusClient()
        self.tools = AIRPORT_TOOLS  # Airport lookup tools
        self.tool_functions = TOOL_FUNCTIONS  # Function mappings

        # Direct OpenAI client for function calling
        self.client = OpenAI(api_key=settings.openai_api_key)

    def execute(self, user_prompt: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the flight search agent logic.

        Args:
            user_prompt: Natural language request from user
            state: Current workflow state (LangGraph state)

        Returns:
            Updated state with flight search results
        """
        try:
            # Step 1: Parse user request using LLM
            parsed_request = self._parse_user_request(user_prompt)
            logger.debug(
                f"Parsed request: {parsed_request.origin_code} -> "
                f"{parsed_request.destination_code} on {parsed_request.departure_date}"
            )

            # Step 2: Convert to FlightSearchRequest
            search_request = self._create_search_request(parsed_request)

            # Step 3: Search flights using Amadeus API
            flight_results = self.amadeus_client.search_flights(search_request)

            # Step 4: Update state with results
            state["parsed_request"] = parsed_request.model_dump()
            state["flight_results"] = flight_results.model_dump()
            state["search_request"] = search_request.model_dump()
            state["user_prompt"] = user_prompt

            logger.debug(
                f"Found {len(flight_results.original_date_offers)} flights for requested date, "
                f"{len(flight_results.alternative_offers)} cheaper alternative dates"
            )

            return state

        except Exception as e:
            logger.error(f"Error in Flight Search Agent: {e}")
            state["error"] = str(e)
            raise

    def _parse_user_request(self, user_prompt: str) -> ParsedFlightRequest:
        """
        Use LLM with tool calling to parse natural language flight request.

        This method uses OpenAI function calling to let the agent use airport lookup tools.

        Args:
            user_prompt: User's natural language request

        Returns:
            Structured ParsedFlightRequest

        Example prompts:
            - "Book a flight from New York to London on December 25th"
            - "I need to fly from LAX to JFK tomorrow at 3 PM"
            - "Find flights from Paris to Tokyo next Monday"
        """
        system_prompt = """You are a flight booking assistant with access to airport lookup tools.

Your task:
1. Identify origin and destination cities from the user request
2. Use the 'get_primary_airport' tool to find IATA codes for both cities
3. Extract departure date and time (if specified)
4. Determine number of passengers and travel class (if specified)

Date handling:
- "today" = current date
- "tomorrow" = current date + 1 day
- "next Monday/Tuesday/etc" = next occurrence of that day
- Specific dates should be in YYYY-MM-DD format

Steps:
1. First, call get_primary_airport for the origin city
2. Then, call get_primary_airport for the destination city
3. After you have both IATA codes, respond with ONLY a JSON object (no markdown, no explanation)

CRITICAL: Your final response must be ONLY a JSON object with these exact fields:
{
  "origin_city": "City name",
  "origin_code": "IATA code from tool",
  "destination_city": "City name",
  "destination_code": "IATA code from tool",
  "departure_date": "YYYY-MM-DD",
  "departure_time": "HH:MM or null",
  "adults": 1,
  "travel_class": "ECONOMY"
}

Do not include any explanation, markdown formatting, or additional text. Return ONLY the JSON object."""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Current date: {datetime.now().strftime('%Y-%m-%d')}\n\nUser request: {user_prompt}"
            }
        ]

        # Run conversation with tool calls
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Check if we should use JSON mode (no tools needed anymore)
            use_json_mode = iteration > 2 and not any(
                msg.get("role") == "tool" for msg in messages[-3:] if isinstance(msg, dict)
            )

            # Call OpenAI with tools
            if use_json_mode:
                # Final call with JSON mode, no tools
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
            else:
                # Regular call with tools
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=0.3
                )

            response_message = response.choices[0].message
            messages.append(response_message)

            # Check if the model wants to call tools
            if response_message.tool_calls and not use_json_mode:
                logger.debug(f"Agent is calling {len(response_message.tool_calls)} tool(s)...")

                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.debug(f"Calling tool: {function_name} with args: {function_args}")

                    # Execute the tool function
                    if function_name in self.tool_functions:
                        function_response = self.tool_functions[function_name](**function_args)
                        logger.debug(f"Tool response: {function_response}")

                        # Add tool response to messages
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(function_response)
                        })
                    else:
                        logger.warning(f"Unknown tool: {function_name}")

            else:
                # No more tool calls - agent has final response
                final_content = response_message.content
                logger.debug(f"Agent finished with final response")

                # Parse the JSON response into our model
                try:
                    # Try to parse as pure JSON first
                    parsed_data = json.loads(final_content)
                    
                    # Validate that required fields are not None
                    required_fields = ["origin_code", "destination_code", "departure_date"]
                    missing_or_none = [field for field in required_fields if not parsed_data.get(field)]
                    
                    if missing_or_none:
                        error_msg = f"LLM returned None/missing values for: {', '.join(missing_or_none)}"
                        logger.error(f"{error_msg}. Response: {final_content}")
                        
                        # If we still have iterations left, ask for clarification
                        if iteration < max_iterations - 1:
                            messages.append({
                                "role": "user",
                                "content": f"Error: {error_msg}. Please use the airport lookup tools to find the correct IATA codes and provide all required fields."
                            })
                            continue
                        else:
                            raise ValueError(
                                f"Could not parse flight request. {error_msg}. "
                                f"Please provide origin city, destination city, and departure date clearly. "
                                f"Example: 'Book a flight from Mumbai to Delhi on November 20th'"
                            )
                    
                    parsed = ParsedFlightRequest.model_validate(parsed_data)
                    return parsed
                except json.JSONDecodeError:
                    # If not pure JSON, try to extract JSON from markdown or text
                    logger.warning("Response is not pure JSON, attempting to extract...")

                    # Try to find JSON in code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', final_content, re.DOTALL)
                    if json_match:
                        try:
                            parsed_data = json.loads(json_match.group(1))
                            parsed = ParsedFlightRequest.model_validate(parsed_data)
                            return parsed
                        except:
                            pass

                    # Try to find raw JSON object
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', final_content, re.DOTALL)
                    if json_match:
                        try:
                            parsed_data = json.loads(json_match.group(0))
                            parsed = ParsedFlightRequest.model_validate(parsed_data)
                            return parsed
                        except:
                            pass

                    # Last resort: ask for JSON explicitly using JSON mode
                    if iteration < max_iterations - 1:
                        logger.warning("Could not extract JSON, requesting explicit JSON format...")
                        messages.append({
                            "role": "user",
                            "content": "Please provide ONLY the JSON object with flight details, no explanation or formatting."
                        })
                        continue

                    # If we're on last iteration, try to construct manually
                    logger.error(f"Failed to extract JSON from response: {final_content[:200]}")
                    raise json.JSONDecodeError("Could not extract valid JSON", final_content, 0)

        raise Exception("Failed to parse user request after maximum iterations")

    def _create_search_request(self, parsed: ParsedFlightRequest) -> FlightSearchRequest:
        """
        Convert parsed request to FlightSearchRequest model.

        Args:
            parsed: Parsed flight request from LLM

        Returns:
            FlightSearchRequest for Amadeus API
        """
        # Parse date
        departure_date = date.fromisoformat(parsed.departure_date)

        # Parse time if provided
        departure_time = None
        if parsed.departure_time:
            try:
                time_parts = parsed.departure_time.split(":")
                departure_time = time(
                    hour=int(time_parts[0]),
                    minute=int(time_parts[1])
                )
            except Exception as e:
                logger.warning(f"Could not parse time '{parsed.departure_time}': {e}")

        return FlightSearchRequest(
            origin=parsed.origin_code,
            destination=parsed.destination_code,
            departure_date=departure_date,
            departure_time=departure_time,
            adults=parsed.adults,
            travel_class=parsed.travel_class,
            max_results=10
        )


# Example usage for testing
if __name__ == "__main__":
    # This allows testing the agent standalone
    agent = FlightSearchAgent()

    # Test with sample prompt
    test_prompt = "I need to fly from New York to Los Angeles on 2025-11-15"

    state = {}
    result = agent.execute(test_prompt, state)

    print("\n" + "="*50)
    print("FLIGHT SEARCH RESULTS")
    print("="*50)
    print(f"Origin: {result['parsed_request']['origin_city']} ({result['parsed_request']['origin_code']})")
    print(f"Destination: {result['parsed_request']['destination_city']} ({result['parsed_request']['destination_code']})")
    print(f"Date: {result['parsed_request']['departure_date']}")
    print(f"Flights found: {len(result['flight_results']['original_date_offers'])}")
