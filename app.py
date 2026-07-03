import gradio as gr
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import flight_search_tool, hotel_search_tool, wiki_tool, save_tool
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

# Define the response model
class TravelPlan(BaseModel):
    user_location: str
    destination: str
    start_date: str
    end_date: str
    budget: float
    flights: str
    hotels: str
    attractions: str
    itinerary: str
    tools_used: list[str]

# Initialize LLM (Google Gemini)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Set up output parser
parser = PydanticOutputParser(pydantic_object=TravelPlan)

# Define prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a travel planner assistant. Plan a trip based on the user's current location, destination, travel dates, and budget (in INR).
            Use provided tools to fetch flight, hotel, and attraction data, ensuring costs stay within the budget.
            All monetary values must be in Indian Rupees (INR). Convert any USD values to INR using 1 USD = 83 INR.
            Format the response to match this strict structure:
            **Travel Plan**
            - **From**: {user_location}
            - **Destination**: {destination}
            - **Dates**: {start_date} to {end_date}
            - **Budget**: ₹{budget}
            - **Prepared for**: Aatif Ahmad
            - **Flights**: [JSON array of objects with keys: Airline, Flight Number, Departure Airport, Arrival Airport, Departure Time, Arrival Time, Price (INR)]
            - **Hotels**: [JSON array of objects with keys: Name, Price per Night (INR), Rating]
            - **Attractions**: [Plain list of attraction names separated by newlines]
            - **Itinerary**: [Plain list of day-by-day plans separated by newlines]
            - **Tools Used**: [Comma-separated list of tools used]
            Ensure flights include at least one entry with all fields (Airline, Flight Number, Departure Airport, Arrival Airport, Departure Time, Arrival Time, Price in INR).
            Ensure hotels include at least one entry with all fields (Name, Price per Night in INR, Rating).
            Return the response in this format and provide no other text:
            {format_instructions}
            """,
        ),
        ("human", "Plan a trip from {user_location} to {destination} from {start_date} to {end_date} with a budget of {budget} INR."),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Define tools
tools = [flight_search_tool, hotel_search_tool, wiki_tool, save_tool]

# Create agent and executor
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Gradio interface function
def plan_trip(user_location, destination, start_date, end_date, budget):
    if not user_location or not destination or not start_date or not end_date or not budget:
        return "Error: All fields are required.", None
    if budget < 0:
        return "Error: Budget must be positive.", None
    try:
        query = {
            "user_location": user_location,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget
        }
        raw_response = agent_executor.invoke(query)
        response = parser.parse(raw_response.get("output"))
        
        # Save itinerary
        itinerary_data = (
            f"Destination: {response.destination}\n"
            f"From: {response.user_location}\n"
            f"Dates: {response.start_date} to {response.end_date}\n"
            f"Budget: ₹{response.budget}\n"
            f"Flights: {response.flights}\n"
            f"Hotels: {response.hotels}\n"
            f"Attractions: {response.attractions}\n"
            f"Itinerary: {response.itinerary}\n"
        )
        save_tool.func(itinerary_data)
        
        # Parse JSON data with error handling
        def safe_parse_json(data):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return []

        flights = safe_parse_json(response.flights) if response.flights.startswith("[") else []
        hotels = safe_parse_json(response.hotels) if response.hotels.startswith("[") else []
        attractions = [attr.strip() for attr in response.attractions.split("\n") if attr.strip()]
        itinerary_lines = [line.strip() for line in response.itinerary.split("\n") if line.strip()]

        # Format flights table
        flights_table = "| Airline | Flight Number | Departure Airport | Arrival Airport | Departure Time | Arrival Time | Price (INR) |\n" \
                       "|---------|---------------|-------------------|-----------------|----------------|--------------|-------------|\n"
        for flight in flights:
            flights_table += f"| {flight.get('Airline', 'N/A')} | {flight.get('Flight Number', 'N/A')} | {flight.get('Departure Airport', 'N/A')} | {flight.get('Arrival Airport', 'N/A')} | {flight.get('Departure Time', 'N/A')} | {flight.get('Arrival Time', 'N/A')} | ₹{flight.get('Price (INR)', 'N/A')} |\n"

        # Format hotels table
        hotels_table = "| Name | Price per Night (INR) | Rating |\n" \
                      "|------|-----------------------|--------|\n"
        for hotel in hotels:
            hotels_table += f"| {hotel.get('Name', 'N/A')} | ₹{hotel.get('Price per Night (INR)', 'N/A')} | {hotel.get('Rating', 'N/A')} |\n"

        # Format attractions list
        attractions_list = "\n".join([f"- {attr}" for attr in attractions])

        # Format itinerary list
        itinerary_list = "\n".join([f"{i+1}. {line}" for i, line in enumerate(itinerary_lines)])

        # Prepare formatted output
        output = (
            f"**Travel Plan**\n\n"
            f"- **From**: {response.user_location}\n"
            f"- **Destination**: {response.destination}\n"
            f"- **Dates**: {response.start_date} to {response.end_date}\n"
            f"- **Budget**: ₹{response.budget}\n"
            f"- **Prepared for**: Aatif Ahmad\n"
            f"- **Flights**:\n{flights_table}\n"
            f"- **Hotels**:\n{hotels_table}\n"
            f"- **Attractions**:\n{attractions_list}\n"
            f"- **Itinerary**:\n{itinerary_list}\n"
            f"- **Tools Used**: {', '.join(response.tools_used)}\n\n"
            f"**Note**: Itinerary saved to itinerary.txt\n"
        )

        # Generate download file
        download_content = (
            f"Travel Plan\n"
            f"From: {response.user_location}\n"
            f"Destination: {response.destination}\n"
            f"Dates: {response.start_date} to {response.end_date}\n"
            f"Budget: ₹{response.budget}\n"
            f"Prepared for: Aatif Ahmad\n"
            f"Flights:\n{flights_table}\n"
            f"Hotels:\n{hotels_table}\n"
            f"Attractions:\n{attractions_list}\n"
            f"Itinerary:\n{itinerary_list}\n"
            f"Tools Used: {', '.join(response.tools_used)}\n"
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}"
        )
        download_file = "itinerary.txt"
        with open(download_file, "w", encoding="utf-8") as f:
            f.write(download_content)
        
        return output, download_file
    except Exception as e:
        return f"Error: Failed to generate plan. {str(e)}", None

# Gradio interface
with gr.Blocks(theme=gr.themes.Default()) as app:
    gr.Markdown(
        """
        # MCP-Based Multi-Agent Travel Planner
        Plan your trip by entering your details below. All costs are in Indian Rupees (INR).
        """
    )
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Enter Trip Details")
            user_location = gr.Textbox(label="Current Location", placeholder="e.g., Delhi", lines=1)
            destination = gr.Textbox(label="Travel Destination", placeholder="e.g., Shimla", lines=1)
            start_date = gr.Textbox(label="Start Date", placeholder="e.g., 2025-07-15", lines=1)
            end_date = gr.Textbox(label="End Date", placeholder="e.g., 2025-07-20", lines=1)
            budget = gr.Number(label="Budget (INR)", value=10000, minimum=0, precision=0)
            submit = gr.Button("Plan Trip", variant="primary")
        with gr.Column(scale=2):
            gr.Markdown("### Your Travel Plan")
            output = gr.Markdown(label="Travel Plan")
            download = gr.File(label="Download Itinerary", file_count="single", interactive=False)
    submit.click(
        fn=plan_trip,
        inputs=[user_location, destination, start_date, end_date, budget],
        outputs=[output, download]
    )

app.launch(server_name="0.0.0.0", server_port=8080)
