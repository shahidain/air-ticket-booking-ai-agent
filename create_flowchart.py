"""
Generate a beautiful flowchart for AI Ticket Booking System workflow.
This creates a clean, professional flow diagram showing the user journey.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib.lines as mlines

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(14, 18))
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor('white')

# Colors
START_COLOR = '#E94B3C'
AGENT_COLOR = '#4A90E2'
DECISION_COLOR = '#F5A623'
END_COLOR = '#50C878'
ARROW_COLOR = '#333333'

y_pos = 17  # Starting Y position

# Title
plt.text(7, y_pos, 'AI TICKET BOOKING SYSTEM',
         fontsize=26, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.6', facecolor='lightgray', edgecolor='black', linewidth=3))

plt.text(7, y_pos - 0.6, 'End-to-End User Workflow',
         fontsize=14, ha='center', style='italic', color='gray')

y_pos -= 2

# START
start = FancyBboxPatch((5.5, y_pos - 0.5), 3, 0.7,
                       boxstyle="round,pad=0.1",
                       facecolor=START_COLOR, edgecolor='black', linewidth=2)
ax.add_patch(start)
plt.text(7, y_pos - 0.15, 'START', fontsize=12, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.4, 'User enters request', fontsize=9, ha='center', color='white', style='italic')

y_pos -= 1.2

# Arrow
arrow = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                       arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow)

y_pos -= 0.8

# AGENT 1: Search
agent1 = FancyBboxPatch((4.5, y_pos - 1), 5, 1.2,
                        boxstyle="round,pad=0.1",
                        facecolor=AGENT_COLOR, edgecolor='black', linewidth=2.5)
ax.add_patch(agent1)

circle1 = Circle((5.3, y_pos - 0.3), 0.25, color='yellow', ec='black', linewidth=2)
ax.add_patch(circle1)
plt.text(5.3, y_pos - 0.3, '1', fontsize=14, fontweight='bold', ha='center', va='center')

plt.text(7, y_pos - 0.3, 'FLIGHT SEARCH AGENT', fontsize=13, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.65, 'Parse request | Search flights | Find alternatives',
         fontsize=9, ha='center', color='white', style='italic')
plt.text(7, y_pos - 0.9, 'Uses: Airport Lookup Tool + Amadeus API',
         fontsize=8, ha='center', color='lightgray')

y_pos -= 1.7

arrow = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                       arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow)

y_pos -= 0.8

# AGENT 2: Presentation
agent2 = FancyBboxPatch((4.5, y_pos - 1), 5, 1.2,
                        boxstyle="round,pad=0.1",
                        facecolor=AGENT_COLOR, edgecolor='black', linewidth=2.5)
ax.add_patch(agent2)

circle2 = Circle((5.3, y_pos - 0.3), 0.25, color='yellow', ec='black', linewidth=2)
ax.add_patch(circle2)
plt.text(5.3, y_pos - 0.3, '2', fontsize=14, fontweight='bold', ha='center', va='center')

plt.text(7, y_pos - 0.3, 'PRESENTATION AGENT', fontsize=13, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.65, 'Format results | Auto-sort | Display table',
         fontsize=9, ha='center', color='white', style='italic')
plt.text(7, y_pos - 0.9, 'Detects user preferences & sorts flights',
         fontsize=8, ha='center', color='lightgray')

y_pos -= 1.7

arrow = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                       arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow)

y_pos -= 0.8

# DECISION: User Selection
decision = mpatches.FancyBboxPatch((4.8, y_pos - 0.8), 4.4, 0.9,
                                   boxstyle="round,pad=0.1",
                                   facecolor=DECISION_COLOR, edgecolor='black', linewidth=2.5)
ax.add_patch(decision)
plt.text(7, y_pos - 0.25, 'USER SELECTS FLIGHT', fontsize=12, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.55, 'Options: Select | View Details | Cancel',
         fontsize=9, ha='center', color='white', style='italic')

y_pos -= 1.3

# Split arrow - Cancel path
arrow_cancel = FancyArrowPatch((4.8, y_pos + 0.2), (2, y_pos - 1),
                              arrowstyle='->', mutation_scale=20, linewidth=2, color='red', linestyle='dashed')
ax.add_patch(arrow_cancel)
plt.text(3.2, y_pos - 0.5, 'Cancel', fontsize=9, ha='center', color='red', fontweight='bold')

# Cancel endpoint
cancel_box = FancyBboxPatch((1, y_pos - 1.4), 2, 0.5,
                           boxstyle="round,pad=0.1",
                           facecolor='#FF6B6B', edgecolor='black', linewidth=2)
ax.add_patch(cancel_box)
plt.text(2, y_pos - 1.15, 'EXIT PROGRAM', fontsize=10, fontweight='bold', ha='center', color='white')

# Main arrow - Continue
arrow_continue = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                                arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow_continue)
plt.text(7.4, y_pos - 0.05, 'Confirm', fontsize=9, ha='left', color='green', fontweight='bold')

y_pos -= 0.8

# AGENT 3: Booking
agent3 = FancyBboxPatch((4.5, y_pos - 1), 5, 1.2,
                        boxstyle="round,pad=0.1",
                        facecolor=AGENT_COLOR, edgecolor='black', linewidth=2.5)
ax.add_patch(agent3)

circle3 = Circle((5.3, y_pos - 0.3), 0.25, color='yellow', ec='black', linewidth=2)
ax.add_patch(circle3)
plt.text(5.3, y_pos - 0.3, '3', fontsize=14, fontweight='bold', ha='center', va='center')

plt.text(7, y_pos - 0.3, 'BOOKING AGENT', fontsize=13, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.65, 'Collect passenger info | Validate ID | Book flight',
         fontsize=9, ha='center', color='white', style='italic')
plt.text(7, y_pos - 0.9, 'AADHAAR/Passport validation | Amadeus booking',
         fontsize=8, ha='center', color='lightgray')

y_pos -= 1.7

arrow = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                       arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow)

y_pos -= 0.8

# AGENT 4: Ticket Generation
agent4 = FancyBboxPatch((4.5, y_pos - 1), 5, 1.2,
                        boxstyle="round,pad=0.1",
                        facecolor=AGENT_COLOR, edgecolor='black', linewidth=2.5)
ax.add_patch(agent4)

circle4 = Circle((5.3, y_pos - 0.3), 0.25, color='yellow', ec='black', linewidth=2)
ax.add_patch(circle4)
plt.text(5.3, y_pos - 0.3, '4', fontsize=14, fontweight='bold', ha='center', va='center')

plt.text(7, y_pos - 0.3, 'TICKET GENERATION AGENT', fontsize=13, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.65, 'Generate ticket | Format details | Create PDF',
         fontsize=9, ha='center', color='white', style='italic')
plt.text(7, y_pos - 0.9, 'Professional ticket with all flight information',
         fontsize=8, ha='center', color='lightgray')

y_pos -= 1.7

arrow = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                       arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow)

y_pos -= 0.8

# AGENT 5: Notification
agent5 = FancyBboxPatch((4.5, y_pos - 1), 5, 1.2,
                        boxstyle="round,pad=0.1",
                        facecolor=AGENT_COLOR, edgecolor='black', linewidth=2.5)
ax.add_patch(agent5)

circle5 = Circle((5.3, y_pos - 0.3), 0.25, color='yellow', ec='black', linewidth=2)
ax.add_patch(circle5)
plt.text(5.3, y_pos - 0.3, '5', fontsize=14, fontweight='bold', ha='center', va='center')

plt.text(7, y_pos - 0.3, 'NOTIFICATION AGENT', fontsize=13, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.65, 'Send confirmation | Email/SMS | Display ticket',
         fontsize=9, ha='center', color='white', style='italic')
plt.text(7, y_pos - 0.9, 'Final confirmation to user',
         fontsize=8, ha='center', color='lightgray')

y_pos -= 1.7

arrow = FancyArrowPatch((7, y_pos + 0.2), (7, y_pos - 0.3),
                       arrowstyle='->', mutation_scale=25, linewidth=3, color=ARROW_COLOR)
ax.add_patch(arrow)

y_pos -= 0.8

# END
end = FancyBboxPatch((5.5, y_pos - 0.5), 3, 0.7,
                     boxstyle="round,pad=0.1",
                     facecolor=END_COLOR, edgecolor='black', linewidth=2)
ax.add_patch(end)
plt.text(7, y_pos - 0.15, 'SUCCESS', fontsize=12, fontweight='bold', ha='center', color='white')
plt.text(7, y_pos - 0.4, 'Booking complete!', fontsize=9, ha='center', color='white', style='italic')

# Add info boxes on sides
info_left = FancyBboxPatch((0.3, 8), 3.5, 4,
                          boxstyle="round,pad=0.15",
                          facecolor='#F0F0F0', edgecolor='black', linewidth=2)
ax.add_patch(info_left)
plt.text(2.05, 11.7, 'TECHNOLOGIES', fontsize=11, fontweight='bold', ha='center')
plt.text(2.05, 10.8, 'LangGraph\nOpenAI GPT-4o-mini\nAmadeus API v12\nPydantic v2\nPython 3.11+\nAsyncIO',
         fontsize=9, ha='center', linespacing=1.8)

info_right = FancyBboxPatch((10.2, 8), 3.5, 4,
                           boxstyle="round,pad=0.15",
                           facecolor='#F0F0F0', edgecolor='black', linewidth=2)
ax.add_patch(info_right)
plt.text(11.95, 11.7, 'KEY FEATURES', fontsize=11, fontweight='bold', ha='center')
plt.text(11.95, 10.8, 'Natural Language\nAuto-Sort Flights\nSafe Exit Options\nID Validation\nCurrency Convert\nAlternative Dates',
         fontsize=9, ha='center', linespacing=1.8)

# Add legend at bottom
legend_box = FancyBboxPatch((0.5, 0.3), 13, 1.2,
                           boxstyle="round,pad=0.1",
                           facecolor='#E8E8E8', edgecolor='black', linewidth=2)
ax.add_patch(legend_box)

plt.text(7, 1.3, 'WORKFLOW LEGEND', fontsize=11, fontweight='bold', ha='center')

# Legend items
legend_items = [
    {'color': START_COLOR, 'label': 'Start/Input', 'x': 1.5},
    {'color': AGENT_COLOR, 'label': 'AI Agent', 'x': 3.8},
    {'color': DECISION_COLOR, 'label': 'User Decision', 'x': 6.1},
    {'color': END_COLOR, 'label': 'Success', 'x': 9.2},
    {'color': '#FF6B6B', 'label': 'Exit/Cancel', 'x': 11.5},
]

for item in legend_items:
    box = Rectangle((item['x'], 0.6), 0.4, 0.3, facecolor=item['color'], edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    plt.text(item['x'] + 0.6, 0.75, item['label'], fontsize=9, va='center', ha='left')

# Add watermark
plt.text(13.5, 0.1, 'AI Ticket Booking System 2025',
         fontsize=7, ha='right', style='italic', color='gray')

plt.tight_layout()

# Save
output_file = 'AI_Ticket_Booking_Flowchart.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print("Flowchart diagram created successfully!")
print("File: " + output_file)
print("Resolution: 4200x5400 pixels (14x18 inches @ 300 DPI)")

# Don't show - just save
# plt.show()
