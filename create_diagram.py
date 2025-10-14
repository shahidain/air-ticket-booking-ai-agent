"""
Generate a beautiful architectural diagram for AI Ticket Booking System.
This script creates a PNG image showing the system architecture.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.lines as mlines

# Create figure with white background
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')
fig.patch.set_facecolor('white')

# Color scheme
COLOR_AGENT = '#4A90E2'      # Blue for agents
COLOR_API = '#50C878'         # Green for APIs
COLOR_MODEL = '#F5A623'       # Orange for models
COLOR_WORKFLOW = '#9013FE'    # Purple for workflow
COLOR_USER = '#E94B3C'        # Red for user
COLOR_EXTERNAL = '#7ED321'    # Light green for external services

# Title
plt.text(8, 11.5, 'AI Ticket Booking System',
         fontsize=28, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', edgecolor='black', linewidth=2))

plt.text(8, 11, 'Multi-Agent Architecture with LangGraph',
         fontsize=14, ha='center', style='italic', color='gray')

# ============= USER LAYER =============
user_box = FancyBboxPatch((0.5, 9.5), 2, 0.8,
                          boxstyle="round,pad=0.1",
                          facecolor=COLOR_USER, edgecolor='black', linewidth=2)
ax.add_patch(user_box)
plt.text(1.5, 9.9, 'User Input', fontsize=12, fontweight='bold', ha='center', color='white')

# ============= WORKFLOW ORCHESTRATION LAYER =============
workflow_box = FancyBboxPatch((5, 9), 6, 1.2,
                              boxstyle="round,pad=0.1",
                              facecolor=COLOR_WORKFLOW, edgecolor='black', linewidth=3)
ax.add_patch(workflow_box)
plt.text(8, 9.9, 'LangGraph Workflow Orchestrator', fontsize=14, fontweight='bold', ha='center', color='white')
plt.text(8, 9.5, 'StateGraph | Agent Coordination | State Management', fontsize=9, ha='center', color='white', style='italic')

# Arrow from user to workflow
arrow1 = FancyArrowPatch((2.5, 9.9), (5, 9.9),
                        arrowstyle='->', mutation_scale=30, linewidth=2.5, color='black')
ax.add_patch(arrow1)
plt.text(3.75, 10.1, 'Natural Language\nRequest', fontsize=8, ha='center')

# ============= 5 AGENTS LAYER =============
agents = [
    {'name': 'Flight Search\nAgent', 'x': 1, 'y': 6.8, 'desc': 'Parse Request\nFind Flights\nCheaper Alternatives'},
    {'name': 'Presentation\nAgent', 'x': 4, 'y': 6.8, 'desc': 'Format Results\nTable Display\nAuto-Sort'},
    {'name': 'Booking\nAgent', 'x': 7, 'y': 6.8, 'desc': 'Collect Info\nBook Flight\nValidate Data'},
    {'name': 'Ticket\nGeneration Agent', 'x': 10.5, 'y': 6.8, 'desc': 'Generate Ticket\nFormat Details\nPrepare PDF'},
    {'name': 'Notification\nAgent', 'x': 13.5, 'y': 6.8, 'desc': 'Send Email\nSMS Alert\nConfirmation'},
]

# Draw agents
for i, agent in enumerate(agents):
    box = FancyBboxPatch((agent['x'], agent['y']), 2.2, 1.4,
                         boxstyle="round,pad=0.1",
                         facecolor=COLOR_AGENT, edgecolor='black', linewidth=2)
    ax.add_patch(box)

    # Agent number circle
    circle = Circle((agent['x'] + 0.3, agent['y'] + 1.2), 0.15, color='yellow', ec='black', linewidth=1.5)
    ax.add_patch(circle)
    plt.text(agent['x'] + 0.3, agent['y'] + 1.2, str(i+1), fontsize=10, fontweight='bold', ha='center', va='center')

    plt.text(agent['x'] + 1.1, agent['y'] + 1.1, agent['name'],
             fontsize=10, fontweight='bold', ha='center', color='white')
    plt.text(agent['x'] + 1.1, agent['y'] + 0.5, agent['desc'],
             fontsize=7, ha='center', color='white', style='italic')

# Arrows connecting agents
for i in range(len(agents) - 1):
    arrow = FancyArrowPatch((agents[i]['x'] + 2.2, agents[i]['y'] + 0.7),
                           (agents[i+1]['x'], agents[i+1]['y'] + 0.7),
                           arrowstyle='->', mutation_scale=20, linewidth=2, color='black')
    ax.add_patch(arrow)

# Arrow from workflow to agents
arrow_to_agents = FancyArrowPatch((8, 9), (8, 8.5),
                                 arrowstyle='->', mutation_scale=30, linewidth=3, color='black')
ax.add_patch(arrow_to_agents)
plt.text(8.5, 8.7, 'Coordinate\nAgents', fontsize=8, ha='center', fontweight='bold')

# ============= TOOLS LAYER =============
plt.text(1.5, 5.9, 'TOOLS', fontsize=11, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', edgecolor='black'))

tools = [
    {'name': 'Airport Lookup', 'x': 0.3, 'y': 5.2},
    {'name': 'Currency Converter', 'x': 2.7, 'y': 5.2},
]

for tool in tools:
    box = FancyBboxPatch((tool['x'], tool['y']), 1.8, 0.5,
                         boxstyle="round,pad=0.05",
                         facecolor='#FFE66D', edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    plt.text(tool['x'] + 0.9, tool['y'] + 0.25, tool['name'],
             fontsize=8, fontweight='bold', ha='center')

# Arrows from search agent to tools
arrow_tool1 = FancyArrowPatch((1.5, 6.8), (1.2, 5.7),
                             arrowstyle='<->', mutation_scale=15, linewidth=1.5, color='black', linestyle='dashed')
ax.add_patch(arrow_tool1)

arrow_tool2 = FancyArrowPatch((2, 6.8), (3.6, 5.7),
                             arrowstyle='<->', mutation_scale=15, linewidth=1.5, color='black', linestyle='dashed')
ax.add_patch(arrow_tool2)

# ============= API CLIENTS LAYER =============
plt.text(8, 5.9, 'API CLIENTS', fontsize=11, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', edgecolor='black'))

api_clients = [
    {'name': 'Amadeus Client', 'x': 6, 'y': 5.2, 'desc': 'Flight Search\nBooking API'},
    {'name': 'OpenAI Client', 'x': 9.5, 'y': 5.2, 'desc': 'LLM Processing\nFunction Calling'},
]

for api in api_clients:
    box = FancyBboxPatch((api['x'], api['y']), 2.2, 0.6,
                         boxstyle="round,pad=0.05",
                         facecolor=COLOR_API, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    plt.text(api['x'] + 1.1, api['y'] + 0.45, api['name'],
             fontsize=9, fontweight='bold', ha='center', color='white')
    plt.text(api['x'] + 1.1, api['y'] + 0.1, api['desc'],
             fontsize=7, ha='center', color='white', style='italic')

# Arrows from agents to APIs
arrow_to_amadeus = FancyArrowPatch((2.1, 6.8), (7.1, 5.8),
                                  arrowstyle='<->', mutation_scale=15, linewidth=2, color='black')
ax.add_patch(arrow_to_amadeus)

arrow_to_openai = FancyArrowPatch((2.1, 7.5), (10.6, 5.8),
                                 arrowstyle='<->', mutation_scale=15, linewidth=2, color='black')
ax.add_patch(arrow_to_openai)

# ============= DATA MODELS LAYER =============
plt.text(14, 5.9, 'DATA MODELS', fontsize=11, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFB84D', edgecolor='black'))

models_box = FancyBboxPatch((12.5, 5.2), 3, 0.6,
                           boxstyle="round,pad=0.05",
                           facecolor=COLOR_MODEL, edgecolor='black', linewidth=2)
ax.add_patch(models_box)
plt.text(14, 5.65, 'Pydantic Models', fontsize=9, fontweight='bold', ha='center', color='white')
plt.text(14, 5.35, 'FlightOffer | PassengerInfo\nBookingConfirmation',
         fontsize=7, ha='center', color='white', style='italic')

# ============= EXTERNAL SERVICES =============
plt.text(8, 3.8, 'EXTERNAL SERVICES', fontsize=12, fontweight='bold', ha='center',
         bbox=dict(boxstyle='round,pad=0.4', facecolor='#C9E4CA', edgecolor='black', linewidth=2))

external = [
    {'name': 'Amadeus\nTravel API', 'x': 4.5, 'y': 2.5, 'icon': '✈️'},
    {'name': 'OpenAI\nGPT-4o-mini', 'x': 8, 'y': 2.5, 'icon': '🤖'},
    {'name': 'Email/SMS\nService', 'x': 11.5, 'y': 2.5, 'icon': '📧'},
]

for ext in external:
    box = FancyBboxPatch((ext['x'], ext['y']), 2, 0.8,
                        boxstyle="round,pad=0.1",
                        facecolor=COLOR_EXTERNAL, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    plt.text(ext['x'] + 1, ext['y'] + 0.55, ext['icon'], fontsize=16, ha='center')
    plt.text(ext['x'] + 1, ext['y'] + 0.2, ext['name'],
             fontsize=8, fontweight='bold', ha='center')

# Arrows to external services
arrow_ext1 = FancyArrowPatch((7.1, 5.2), (5.5, 3.3),
                            arrowstyle='<->', mutation_scale=20, linewidth=2.5, color='darkgreen')
ax.add_patch(arrow_ext1)

arrow_ext2 = FancyArrowPatch((10.6, 5.2), (9, 3.3),
                            arrowstyle='<->', mutation_scale=20, linewidth=2.5, color='darkblue')
ax.add_patch(arrow_ext2)

arrow_ext3 = FancyArrowPatch((14.5, 6.8), (12.5, 3.3),
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='darkred')
ax.add_patch(arrow_ext3)

# ============= KEY FEATURES BOX =============
features_box = FancyBboxPatch((0.5, 0.2), 7, 1.8,
                             boxstyle="round,pad=0.1",
                             facecolor='#F0F0F0', edgecolor='black', linewidth=2)
ax.add_patch(features_box)

plt.text(4, 1.85, '🌟 KEY FEATURES', fontsize=11, fontweight='bold', ha='center')
features_text = """
✅ Natural Language Processing | ✅ Multi-Agent Coordination
✅ OpenAI Function Calling | ✅ Intelligent Flight Sorting
✅ Safe Exit Options | ✅ AADHAAR/Passport Validation
✅ Currency Conversion | ✅ Alternative Date Search
"""
plt.text(4, 1.1, features_text, fontsize=8, ha='center', va='center')

# ============= TECH STACK BOX =============
tech_box = FancyBboxPatch((8.5, 0.2), 7, 1.8,
                         boxstyle="round,pad=0.1",
                         facecolor='#F0F0F0', edgecolor='black', linewidth=2)
ax.add_patch(tech_box)

plt.text(12, 1.85, '⚙️ TECH STACK', fontsize=11, fontweight='bold', ha='center')
tech_text = """
🐍 Python 3.11+ | 🔗 LangGraph | 🤖 OpenAI GPT-4o-mini
✈️ Amadeus API v12 | 📋 Pydantic v2 | 🔄 AsyncIO
🛠️ Function Calling | 💾 State Management
"""
plt.text(12, 1.1, tech_text, fontsize=8, ha='center', va='center')

# ============= LEGEND =============
legend_elements = [
    mlines.Line2D([0], [0], marker='s', color='w', markerfacecolor=COLOR_AGENT,
                  markersize=10, label='AI Agents', markeredgecolor='black'),
    mlines.Line2D([0], [0], marker='s', color='w', markerfacecolor=COLOR_API,
                  markersize=10, label='API Clients', markeredgecolor='black'),
    mlines.Line2D([0], [0], marker='s', color='w', markerfacecolor=COLOR_EXTERNAL,
                  markersize=10, label='External Services', markeredgecolor='black'),
    mlines.Line2D([0], [0], marker='s', color='w', markerfacecolor=COLOR_WORKFLOW,
                  markersize=10, label='Workflow Engine', markeredgecolor='black'),
]

# Add watermark
plt.text(15.5, 0.1, '© 2025 AI Ticket Booking System',
         fontsize=7, ha='right', style='italic', color='gray')

plt.tight_layout()

# Save the diagram
output_file = 'AI_Ticket_Booking_Architecture.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"✅ Diagram saved as: {output_file}")
print(f"📊 Resolution: 4800x3600 pixels (16x12 inches @ 300 DPI)")
print(f"🎨 Format: PNG with white background")

plt.show()
