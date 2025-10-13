"""
Agent 5: Notification Agent

This agent:
1. Receives formatted ticket from Agent 4
2. Presents final ticket to user
3. Provides booking reference and next steps
4. Completes the booking workflow
5. (In production: would send email, SMS, save to database)
"""

from typing import Dict, Any
from api.openai_client import OpenAIClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationAgent:
    """
    Agent 5: Final notification and ticket delivery.

    This is the last agent in the workflow. It presents the
    completed ticket to the user and confirms the booking.
    """

    def __init__(self):
        """Initialize the agent with OpenAI client."""
        self.openai_client = OpenAIClient()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the notification agent logic.

        Args:
            state: Current workflow state with formatted ticket

        Returns:
            Updated state marking completion
        """
        logger.debug("Notification Agent executing")

        try:
            # Extract formatted ticket from state
            formatted_ticket = state.get("formatted_ticket", "")
            booking_confirmation = state.get("booking_confirmation", {})

            # Display the ticket to user
            self._display_ticket(formatted_ticket, booking_confirmation)

            # Mark workflow as complete
            state["workflow_complete"] = True
            state["completion_time"] = str(__import__('datetime').datetime.now())

            logger.info("Notification sent successfully. Workflow complete.")

            return state

        except Exception as e:
            logger.error(f"Error in Notification Agent: {e}")
            state["error"] = str(e)
            raise

    def _display_ticket(
        self,
        formatted_ticket: str,
        booking_confirmation: Dict[str, Any]
    ) -> None:
        """
        Display the ticket to the user with confirmation message.

        In production, this would:
        - Send email with ticket PDF
        - Send SMS with booking reference
        - Save to user's account/database
        - Trigger mobile app notification
        - Create calendar event

        Args:
            formatted_ticket: The formatted ticket string
            booking_confirmation: Booking details
        """
        print("\n\n")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "         🎉 BOOKING CONFIRMED - YOUR TICKET IS READY! 🎉         ".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print("\n")

        # Display the formatted ticket
        print(formatted_ticket)

        print("\n")
        print("─" * 80)

        # Additional confirmation message
        confirmation_message = self._generate_confirmation_message(booking_confirmation)
        print(confirmation_message)

        print("─" * 80)
        print("\n")

        # In production, save ticket or send via email
        self._mock_email_notification(booking_confirmation)

    def _generate_confirmation_message(
        self,
        booking_confirmation: Dict[str, Any]
    ) -> str:
        """
        Generate a friendly confirmation message using LLM.

        Args:
            booking_confirmation: Booking details

        Returns:
            Confirmation message string
        """
        booking_ref = booking_confirmation.get("booking_reference", "N/A")

        instruction = """Generate a brief, friendly confirmation message for a flight booking.

Include:
1. Thank the customer
2. Mention the booking reference
3. Remind them to check email for ticket
4. Mention next steps (check-in, arrive early)
5. Wish them a good flight

Keep it warm, professional, and concise (3-4 sentences)."""

        data = {
            "booking_reference": booking_ref,
            "status": booking_confirmation.get("status", "CONFIRMED")
        }

        message = self.openai_client.format_response(
            data=data,
            format_instruction=instruction,
            temperature=0.7
        )

        return message

    def _mock_email_notification(self, booking_confirmation: Dict[str, Any]) -> None:
        """
        Simulate sending email notification.

        In production, this would:
        - Use SendGrid, AWS SES, or similar service
        - Send HTML email with ticket attachment
        - Include booking reference and QR code

        Args:
            booking_confirmation: Booking details
        """
        passengers = booking_confirmation.get("passengers", [])
        emails = [p.get("email") for p in passengers if p.get("email")]

        if emails:
            logger.info(f"📧 [SIMULATED] Email sent to: {', '.join(emails)}")
            print(f"\n📧 Ticket sent to: {', '.join(emails)}")
        else:
            logger.info("📧 [SIMULATED] Email would be sent (no email addresses in demo)")

    def send_sms_notification(self, phone: str, booking_ref: str) -> None:
        """
        Simulate sending SMS notification.

        In production, use Twilio, AWS SNS, or similar.

        Args:
            phone: Phone number
            booking_ref: Booking reference
        """
        logger.info(f"📱 [SIMULATED] SMS sent to {phone}: Your booking {booking_ref} is confirmed!")


# Example usage for testing
if __name__ == "__main__":
    mock_ticket = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                    ✈️ E-TICKET / BOARDING PASS                      ║
    ╠══════════════════════════════════════════════════════════════════════╣
    ║  Booking Reference: ABC123XYZ                                        ║
    ║  Status: CONFIRMED                                                   ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """

    mock_booking = {
        "booking_reference": "ABC123XYZ",
        "status": "CONFIRMED",
        "passengers": [
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            }
        ]
    }

    mock_state = {
        "formatted_ticket": mock_ticket,
        "booking_confirmation": mock_booking
    }

    agent = NotificationAgent()
    print("Notification Agent ready for testing")
    # Uncomment to test:
    # result = agent.execute(mock_state)
