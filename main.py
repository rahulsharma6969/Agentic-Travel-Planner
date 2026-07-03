from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import flight_search_tool, hotel_search_tool, wiki_tool, save_tool
import os

load_dotenv()

# Define the response model
class TravelPlan(BaseModel):
    destination: str
    dates: str
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
            You are a travel planner assistant. Plan a trip based on the user's destination and dates.
            Use provided tools to fetch flight, hotel, and attraction data, then create a simple itinerary.
            Return the response in this format and provide no other text:
            {format_instructions}
            """,
        ),
        ("human", "Plan a trip to {destination} for {dates}."),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Define tools
tools = [flight_search_tool, hotel_search_tool, wiki_tool, save_tool]

# Create agent and executor
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Main execution
if __name__ == "__main__":
    destination = input("Enter destination (e.g., Paris): ")
    dates = input("Enter travel dates (e.g., 2025-08-01 to 2025-08-03): ")
    query = f"Plan a trip to {destination} for {dates}."
    
    try:
        raw_response = agent_executor.invoke({"destination": destination, "dates": dates})
        structured_response = parser.parse(raw_response.get("output"))

        # Print structured response
        print("\nTravel Plan:")
        print(f"Destination: {structured_response.destination}")
        print(f"Dates: {structured_response.dates}")
        print(f"Flights: {structured_response.flights}")
        print(f"Hotels: {structured_response.hotels}")
        print(f"Attractions: {structured_response.attractions}")
        print(f"Itinerary: {structured_response.itinerary}")
        print(f"Tools Used: {structured_response.tools_used}")

        # Save itinerary
        itinerary_data = (
            f"Destination: {structured_response.destination}\n"
            f"Dates: {structured_response.dates}\n"
            f"Flights: {structured_response.flights}\n"
            f"Hotels: {structured_response.hotels}\n"
            f"Attractions: {structured_response.attractions}\n"
            f"Itinerary: {structured_response.itinerary}"
        )
        save_tool.func(itinerary_data)

    except Exception as e:
        print(f"Error: {e}, Raw Response: {raw_response}")