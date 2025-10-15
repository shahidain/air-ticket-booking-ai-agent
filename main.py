"""
Main entry point for the AI Ticket Booking System.
This script initializes the booking workflow and handles user interactions.
"""

import asyncio
import sys
import io

# Fix Windows console encoding issues - MUST be before any imports that might print
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from workflows.booking_workflow import BookingWorkflow
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def main():
    """Main function to run the flight booking system."""
    print("\n" + "="*60)
    print("WELCOME TO AI TICKET BOOKING SYSTEM")
    print("="*60)
    print("I can help you find and book flights using natural language!")
    print("Examples:")
    print("   - 'Find a cheap flight from New York to London'")
    print("   - 'Book a direct flight from Delhi to Mumbai tomorrow'")
    print("   - 'I need an early morning flight from Tokyo to Sydney'")
    print("\nYou can type 'cancel' at any time to exit the program")
    print("="*60)

    # Initialize the booking workflow
    workflow = BookingWorkflow()

    # Example user prompt
    user_prompt = input("\nEnter your flight booking request: ").strip()

    # Check for immediate cancel
    if user_prompt.lower() in ['cancel', 'exit', 'quit']:
        print("\nGoodbye! Come back anytime to book your flights.")
        return

    try:
        # Execute the workflow
        result = await workflow.run(user_prompt)

        print("\n" + "="*50)
        print("BOOKING COMPLETED")
        print("="*50)

    except KeyboardInterrupt:
        print("\n" + "="*50)
        print("BOOKING CANCELLED")
        print("="*50)
        print("You can restart the program anytime to make a new booking.")
        
    except Exception as e:
        logger.error(f"Error during booking process: {e}")
        print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
