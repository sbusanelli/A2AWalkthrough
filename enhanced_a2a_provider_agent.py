import asyncio
import json
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Any

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from langchain.agents import create_agent
from langchain_core.prompts import PromptTemplate
from langchain_litellm import ChatLiteLLM
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StdioConnection
from langgraph_a2a_server import A2AServer
from langchain_core.tools import Tool

from helpers import setup_env

# Load doctors data
doctors: list = json.loads(Path("data/doctors.json").read_text())

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


class EnhancedProviderAgent:
    """Enhanced Provider Agent with intelligent reasoning capabilities."""
    
    def __init__(self):
        self.mcp_client = None
        self.agent = None
        self.setup_client()
        
    def setup_client(self):
        """Setup MCP client with enhanced tools."""
        self.mcp_client = MultiServerMCPClient(
            {
                "enhanced_healthcare_providers": StdioConnection(
                    transport="stdio",
                    command="uv",
                    args=["run", "enhanced_mcpserver.py"],
                )
            }
        )
    
    def parse_user_query(self, query: str) -> Dict[str, Any]:
        """Intelligently parse user query for location, specialty, insurance, etc."""
        parsed = {
            "location": {"city": None, "state": None},
            "specialty_keywords": [],
            "insurance_plan": None,
            "urgency": False,
            "preferences": {}
        }
        
        # Extract location
        city_patterns = [
            r'(\w+)\s*,\s*(\w{2})',  # "Austin, TX"
            r'(\w+)\s+Texas',        # "Austin Texas"
            r'in\s+(\w+)',           # "in Austin"
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    parsed["location"]["city"] = match.group(1)
                    parsed["location"]["state"] = match.group(2)
                else:
                    parsed["location"]["city"] = match.group(1)
                break
        
        # Extract insurance
        insurance_keywords = ["blue cross", "aetna", "unitedhealth", "cigna", "humana", "medicare", "medicaid"]
        for insurance in insurance_keywords:
            if insurance.lower() in query.lower():
                parsed["insurance_plan"] = insurance
                break
        
        # Detect urgency
        urgency_words = ["urgent", "emergency", "asap", "immediately", "right away"]
        if any(word in query.lower() for word in urgency_words):
            parsed["urgency"] = True
        
        return parsed
    
    def create_intelligent_tools(self) -> List[Tool]:
        """Create intelligent tools that combine multiple MCP operations."""
        
        async def intelligent_provider_search(query: str) -> str:
            """Intelligently search for providers based on natural language query."""
            try:
                # Parse the query
                parsed = self.parse_user_query(query)
                
                # Get base provider list
                tools = await self.mcp_client.get_tools()
                list_doctors_tool = next((tool for tool in tools if tool.name == "list_doctors"), None)
                
                if not list_doctors_tool:
                    return "Error: list_doctors tool not available"
                
                # Search by location
                city = parsed["location"]["city"]
                state = parsed["location"]["state"]
                
                if city or state:
                    base_providers = await list_doctors_tool.ainvoke({
                        "state": state,
                        "city": city
                    })
                else:
                    base_providers = doctors  # Fallback to all doctors
                
                # Filter by specialty keywords
                specialty_tool = next((tool for tool in tools if tool.name == "filter_by_specialty_keywords"), None)
                if specialty_tool:
                    filtered_providers = await specialty_tool.ainvoke({
                        "query": query,
                        "providers": base_providers
                    })
                else:
                    filtered_providers = base_providers
                
                # Calculate distances (mock user location based on query city)
                distance_tool = next((tool for tool in tools if tool.name == "calculate_distance"), None)
                if distance_tool and city:
                    # Mock coordinates for the city
                    city_coords = self.get_city_coordinates(city, state)
                    providers_with_distance = await distance_tool.ainvoke({
                        "user_location": city_coords,
                        "provider_addresses": filtered_providers
                    })
                else:
                    providers_with_distance = filtered_providers
                
                # Check insurance compatibility
                insurance_tool = next((tool for tool in tools if tool.name == "check_insurance_compatibility"), None)
                if insurance_tool and parsed["insurance_plan"]:
                    provider_ids = [p["id"] for p in providers_with_distance]
                    insurance_results = await insurance_tool.ainvoke({
                        "provider_ids": provider_ids,
                        "insurance_plan": parsed["insurance_plan"]
                    })
                    
                    # Keep only compatible providers
                    compatible_ids = [p["id"] for p in insurance_results["compatible"]]
                    final_providers = [p for p in providers_with_distance if p["id"] in compatible_ids]
                else:
                    final_providers = providers_with_distance
                
                # Rank providers
                ranking_tool = next((tool for tool in tools if tool.name == "rank_providers_by_criteria"), None)
                if ranking_tool:
                    ranked_providers = await ranking_tool.ainvoke({
                        "providers": final_providers,
                        "criteria": {
                            "insurance_plan": parsed["insurance_plan"],
                            "urgency": parsed["urgency"]
                        }
                    })
                else:
                    ranked_providers = final_providers
                
                # Format results
                return self.format_provider_results(ranked_providers[:5], parsed)
                
            except Exception as e:
                return f"Error searching for providers: {str(e)}"
        
        async def check_provider_details(provider_id: str) -> str:
            """Get detailed information about a specific provider."""
            try:
                tools = await self.mcp_client.get_tools()
                availability_tool = next((tool for tool in tools if tool.name == "check_provider_availability"), None)
                
                if availability_tool:
                    availability = await availability_tool.ainvoke({
                        "provider_ids": [provider_id],
                        "date_range": "this_week"
                    })
                    
                    provider = next((doc for doc in doctors if doc["id"] == provider_id), None)
                    if provider:
                        return self.format_provider_details(provider, availability.get(provider_id, {}))
                    else:
                        return f"Provider with ID {provider_id} not found."
                else:
                    return "Availability tool not available"
                    
            except Exception as e:
                return f"Error getting provider details: {str(e)}"
        
        return [
            Tool(
                name="intelligent_provider_search",
                description="Search for healthcare providers using natural language with intelligent filtering and ranking",
                func=intelligent_provider_search
            ),
            Tool(
                name="check_provider_details", 
                description="Get detailed information about a specific provider including availability",
                func=check_provider_details
            )
        ]
    
    def get_city_coordinates(self, city: str, state: str) -> Dict[str, float]:
        """Get coordinates for a city (mock implementation)."""
        city_coordinates = {
            "austin": {"lat": 30.2672, "lon": -97.7431},
            "boston": {"lat": 42.3601, "lon": -71.0589},
            "atlanta": {"lat": 33.7490, "lon": -84.3880},
            "seattle": {"lat": 47.6062, "lon": -122.3321},
            "chicago": {"lat": 41.8781, "lon": -87.6298},
            "houston": {"lat": 29.7604, "lon": -95.3698},
            "denver": {"lat": 39.7392, "lon": -104.9903},
            "los angeles": {"lat": 34.0522, "lon": -118.2437},
            "miami": {"lat": 25.7617, "lon": -80.1918},
            "nashville": {"lat": 36.1627, "lon": -86.7816},
            "phoenix": {"lat": 33.4484, "lon": -112.0740}
        }
        
        city_lower = city.lower()
        return city_coordinates.get(city_lower, {"lat": 0, "lon": 0})
    
    def format_provider_results(self, providers: List[Dict], parsed_query: Dict) -> str:
        """Format provider search results in a user-friendly way."""
        if not providers:
            return "No providers found matching your criteria. Try adjusting your search terms or location."
        
        response = f"Found {len(providers)} healthcare providers matching your criteria:\n\n"
        
        for i, provider in enumerate(providers, 1):
            distance = provider.get("distance_miles", "Unknown")
            accepting = "✅ Accepting new patients" if provider.get("accepts_new_patients") else "❌ Not accepting new patients"
            
            response += f"**{i}. {provider['name']}**\n"
            response += f"   Specialty: {provider['specialty']}\n"
            response += f"   Location: {provider['address']['street']}, {provider['address']['city']}, {provider['address']['state']}\n"
            response += f"   Distance: {distance} miles\n"
            response += f"   Phone: {provider['phone']}\n"
            response += f"   Status: {accepting}\n"
            
            if parsed_query.get("insurance_plan"):
                insurance_accepted = parsed_query["insurance_plan"] in provider.get("insurance_accepted", [])
                insurance_status = "✅ Accepts your insurance" if insurance_accepted else "❌ Does not accept your insurance"
                response += f"   Insurance: {insurance_status}\n"
            
            response += "\n"
        
        # Add helpful suggestions
        if len(providers) > 0:
            response += "\n💡 **Next Steps:**\n"
            response += "• Call providers directly to schedule appointments\n"
            response += "• Verify insurance coverage when calling\n"
            response += "• Ask about new patient requirements\n"
            
            if parsed_query.get("urgency"):
                response += "• For urgent care needs, consider emergency services or urgent care centers\n"
        
        return response
    
    def format_provider_details(self, provider: Dict, availability: Dict) -> str:
        """Format detailed provider information."""
        response = f"**{provider['name']}**\n\n"
        response += f"🏥 **Specialty:** {provider['specialty']}\n"
        response += f"📍 **Address:** {provider['address']['street']}, {provider['address']['city']}, {provider['address']['state']} {provider['address']['zip_code']}\n"
        response += f"📞 **Phone:** {provider['phone']}\n"
        response += f"📧 **Email:** {provider['email']}\n"
        response += f"🎓 **Experience:** {provider['years_experience']} years\n"
        response += f"🏆 **Board Certified:** {'Yes' if provider['board_certified'] else 'No'}\n"
        response += f"👥 **Accepting New Patients:** {'Yes' if provider['accepts_new_patients'] else 'No'}\n\n"
        
        response += "**Hospital Affiliations:**\n"
        for hospital in provider['hospital_affiliations']:
            response += f"• {hospital}\n"
        response += "\n"
        
        response += "**Education:**\n"
        education = provider['education']
        response += f"• Medical School: {education['medical_school']}\n"
        response += f"• Residency: {education['residency']}\n"
        if education['fellowship'] != 'None':
            response += f"• Fellowship: {education['fellowship']}\n"
        response += "\n"
        
        response += "**Languages:**\n"
        for lang in provider['languages']:
            response += f"• {lang}\n"
        response += "\n"
        
        response += "**Insurance Accepted:**\n"
        for insurance in provider['insurance_accepted']:
            response += f"• {insurance}\n"
        response += "\n"
        
        if availability:
            response += "**Availability:**\n"
            response += f"• Next Available: {availability['next_available']}\n"
            response += f"• Available Times: {', '.join(availability['available_times'])}\n"
        
        return response
    
    def create_agent(self) -> 'CompiledStateGraph':
        """Create the enhanced LangChain agent."""
        llm = ChatLiteLLM(
            model="gemini/gemini-3.1-flash-lite-preview",
            max_tokens=1500,
            temperature=0.1
        )
        
        intelligent_tools = self.create_intelligent_tools()
        
        # Enhanced system prompt
        system_prompt = """You are an intelligent healthcare provider assistant with advanced reasoning capabilities. 

Your role is to help users find the best healthcare providers for their needs using your intelligent search and analysis tools.

CAPABILITIES:
- Natural language query understanding (e.g., "I need a psychiatrist in Austin who takes Blue Cross")
- Multi-factor provider ranking (distance, availability, insurance compatibility, experience)
- Intelligent filtering based on medical specialty keywords
- Personalized recommendations based on user preferences

RESPONSE GUIDELINES:
1. Always use the intelligent_provider_search tool for finding providers
2. Provide detailed, actionable information
3. Consider user context (urgency, insurance, location preferences)
4. Offer helpful next steps and alternatives
5. Be empathetic and professional

When users ask for provider details, use the check_provider_details tool for comprehensive information.

You excel at understanding complex queries like:
- "I need a female cardiologist near me who accepts Aetna"
- "Find a psychiatrist for my teenager in Austin"
- "Urgent: I need mental health help this week"

Your intelligent reasoning makes finding the right healthcare provider much easier than simple database searches."""

        agent = create_agent(
            llm=llm,
            tools=intelligent_tools,
            name="EnhancedHealthcareProviderAgent",
            system_prompt=system_prompt
        )
        
        return agent


def main() -> None:
    print("Running Enhanced Healthcare Provider Agent")
    setup_env()

    HOST = os.getenv("AGENT_HOST", "localhost")
    PORT = int(os.getenv("PROVIDER_AGENT_PORT"))

    # Create enhanced agent
    enhanced_agent = EnhancedProviderAgent()
    agent = enhanced_agent.create_agent()

    agent_card = AgentCard(
        name="EnhancedHealthcareProviderAgent",
        description="Intelligent healthcare provider search with advanced reasoning, multi-factor ranking, and personalized recommendations.",
        url=f"http://{HOST}:{PORT}/",
        version="2.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id="intelligent_provider_search",
                name="Intelligent Provider Search",
                description="Advanced provider search with natural language understanding and intelligent ranking.",
                tags=["healthcare", "providers", "ai", "search", "ranking"],
                examples=[
                    "I need a psychiatrist in Austin who takes Blue Cross",
                    "Find a female cardiologist near me who accepts Aetna",
                    "Urgent: I need mental health help this week in Boston",
                    "Looking for a pediatrician for my child in Houston"
                ],
            ),
            AgentSkill(
                id="detailed_provider_info",
                name="Detailed Provider Information", 
                description="Comprehensive provider details including availability and credentials.",
                tags=["healthcare", "providers", "details", "availability"],
                examples=[
                    "Tell me more about Dr. Sarah Mitchell",
                    "What are Dr. James Rodriguez's qualifications?",
                    "When is Dr. Emily Chen available?"
                ],
            )
        ],
    )

    server = A2AServer(
        graph=agent,
        agent_card=agent_card,
        host=HOST,
        port=PORT,
    )

    server.serve(app_type="starlette")


if __name__ == "__main__":
    main()
