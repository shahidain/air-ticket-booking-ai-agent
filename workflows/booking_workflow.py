"""
LangGraph Workflow Orchestrator

This module uses LangGraph to orchestrate the multi-agent booking workflow:
1. Flight Search Agent
2. Flight Presentation Agent
3. User Selection (Human-in-the-loop)
4. Booking Agent
5. Ticket Generation Agent
6. Notification Agent

The workflow handles state management and agent sequencing.
"""

from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator

from agents.flight_search_agent import FlightSearchAgent
from agents.presentation_agent import FlightPresentationAgent
from agents.booking_agent import BookingAgent
from agents.ticket_generation_agent import TicketGenerationAgent
from agents.notification_agent import NotificationAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BookingState(TypedDict, total=False):
    """
    State schema for the booking workflow.

    This defines all data that flows between agents.
    """
    # Input
    user_prompt: str

    # Agent 1 outputs
    parsed_request: Dict[str, Any]
    search_request: Dict[str, Any]
    flight_results: Dict[str, Any]

    # Agent 2 outputs
    presentation: str

    # User selection
    selected_offer: Dict[str, Any]
    selection_number: int

    # Agent 3 outputs
    passengers: list[Dict[str, Any]]
    booking_confirmation: Dict[str, Any]

    # Agent 4 outputs
    formatted_ticket: str

    # Agent 5 outputs
    workflow_complete: bool
    completion_time: str

    # Error handling
    error: str

    # Messages log (for debugging)
    messages: Annotated[list, operator.add]


class BookingWorkflow:
    """
    Main workflow orchestrator using LangGraph.

    This class builds and manages the agent graph.
    """

    def __init__(self):
        """Initialize the workflow and all agents."""
        logger.info("Initializing Booking Workflow...")

        # Initialize all agents
        self.search_agent = FlightSearchAgent()
        self.presentation_agent = FlightPresentationAgent()
        self.booking_agent = BookingAgent()
        self.ticket_agent = TicketGenerationAgent()
        self.notification_agent = NotificationAgent()

        # Build the workflow graph
        self.graph = self._build_graph()

        logger.info("Booking Workflow initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.

        Returns:
            Compiled StateGraph
        """
        # Create the graph
        workflow = StateGraph(BookingState)

        # Add nodes (agents)
        workflow.add_node("search", self._search_node)
        workflow.add_node("present", self._present_node)
        workflow.add_node("get_selection", self._selection_node)
        workflow.add_node("book", self._booking_node)
        workflow.add_node("generate_ticket", self._ticket_generation_node)
        workflow.add_node("notify", self._notification_node)

        # Define the flow
        workflow.set_entry_point("search")

        # Add edges (sequential flow)
        workflow.add_edge("search", "present")
        workflow.add_edge("present", "get_selection")
        workflow.add_edge("get_selection", "book")
        workflow.add_edge("book", "generate_ticket")
        workflow.add_edge("generate_ticket", "notify")
        workflow.add_edge("notify", END)

        # Compile the graph
        # Using memory saver for checkpointing
        memory = MemorySaver()
        compiled_graph = workflow.compile(checkpointer=memory)

        return compiled_graph

    # Node functions - these wrap each agent's execute method

    def _search_node(self, state: BookingState) -> BookingState:
        """Node for Flight Search Agent."""
        logger.info("Executing search node...")
        try:
            state = self.search_agent.execute(state["user_prompt"], state)
            state.setdefault("messages", []).append("Flight search completed")
            return state
        except Exception as e:
            logger.error(f"Search node failed: {e}")
            state["error"] = str(e)
            raise

    def _present_node(self, state: BookingState) -> BookingState:
        """Node for Flight Presentation Agent."""
        logger.info("Executing presentation node...")
        try:
            state = self.presentation_agent.execute(state)
            state.setdefault("messages", []).append("Flight options presented")
            return state
        except Exception as e:
            logger.error(f"Presentation node failed: {e}")
            state["error"] = str(e)
            raise

    def _selection_node(self, state: BookingState) -> BookingState:
        """Node for user selection (human-in-the-loop)."""
        logger.info("Waiting for user selection...")
        try:
            state = self.presentation_agent.get_user_selection(state)
            state.setdefault("messages", []).append(
                f"User selected option {state.get('selection_number')}"
            )
            return state
        except Exception as e:
            logger.error(f"Selection node failed: {e}")
            state["error"] = str(e)
            raise

    def _booking_node(self, state: BookingState) -> BookingState:
        """Node for Booking Agent."""
        logger.info("Executing booking node...")
        try:
            state = self.booking_agent.execute(state)
            state.setdefault("messages", []).append("Booking completed")
            return state
        except Exception as e:
            logger.error(f"Booking node failed: {e}")
            state["error"] = str(e)
            raise

    def _ticket_generation_node(self, state: BookingState) -> BookingState:
        """Node for Ticket Generation Agent."""
        logger.debug("Executing ticket generation node...")
        try:
            state = self.ticket_agent.execute(state)
            state.setdefault("messages", []).append("Ticket generated")
            return state
        except Exception as e:
            logger.error(f"Ticket generation node failed: {e}")
            state["error"] = str(e)
            raise

    def _notification_node(self, state: BookingState) -> BookingState:
        """Node for Notification Agent."""
        logger.debug("Executing notification node...")
        try:
            state = self.notification_agent.execute(state)
            state.setdefault("messages", []).append("Notification sent")
            return state
        except Exception as e:
            logger.error(f"Notification node failed: {e}")
            state["error"] = str(e)
            raise

    async def run(self, user_prompt: str) -> Dict[str, Any]:
        """
        Run the complete booking workflow.

        Args:
            user_prompt: User's natural language booking request

        Returns:
            Final state with booking confirmation

        Raises:
            Exception: If any agent fails
        """
        logger.info(f"Starting workflow with prompt: {user_prompt}")

        # Initialize state
        initial_state: BookingState = {
            "user_prompt": user_prompt,
            "messages": ["Workflow started"]
        }

        # Execute the graph
        config = {"configurable": {"thread_id": "1"}}

        try:
            final_state = None
            for state in self.graph.stream(initial_state, config):
                # Stream returns dict with node name as key
                logger.debug(f"Current state: {list(state.keys())}")
                final_state = state

            # Extract the actual state (last value in the dict)
            if final_state:
                final_state = list(final_state.values())[0]

            logger.info("Workflow completed successfully")
            return final_state

        except KeyboardInterrupt:
            logger.info("Workflow cancelled by user")
            # Re-raise KeyboardInterrupt to be handled by main.py
            raise
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            raise

    def visualize(self, output_path: str = "workflow_graph.png") -> None:
        """
        Visualize the workflow graph.

        Requires: pip install pygraphviz

        Args:
            output_path: Path to save the visualization
        """
        try:
            from IPython.display import Image, display

            # Generate visualization
            graph_image = self.graph.get_graph().draw_mermaid_png()

            # Save to file
            with open(output_path, "wb") as f:
                f.write(graph_image)

            logger.info(f"Workflow graph saved to {output_path}")

        except ImportError:
            logger.warning(
                "Visualization requires: pip install pygraphviz"
            )
        except Exception as e:
            logger.error(f"Failed to visualize graph: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio

    workflow = BookingWorkflow()

    # Test with sample prompt
    test_prompt = "Book a flight from New York to Los Angeles on 2025-11-20"

    async def test_workflow():
        result = await workflow.run(test_prompt)
        print("\nWorkflow Messages:")
        for msg in result.get("messages", []):
            print(f"  - {msg}")

    asyncio.run(test_workflow())
