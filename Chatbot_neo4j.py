#!/usr/bin/env python3
import os
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv

# --- LangChain Imports ---
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_classic.agents import AgentExecutor, create_react_agent
# We use ChatGroq since you provided a Groq Key
from langchain_groq import ChatGroq

# --- Neo4j Import Logic ---
try:
    from langchain_neo4j import Neo4jGraph
except ModuleNotFoundError:
    from langchain_community.graphs import Neo4jGraph

# --- Load Credentials ---
full_path_to_env = Path('.env')
load_dotenv(dotenv_path=full_path_to_env)

groq_api_key = os.getenv("GROQ_API_KEY")
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# --- Global Initialization ---
# Using Llama 3.3 on Groq (Fast & Smart)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=groq_api_key,
    temperature=0,
    stop_sequences=["\nObservation:", "Observation:"]
)

graph = None

# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

if all([groq_api_key, neo4j_uri, neo4j_username, neo4j_password]):
    try:
        graph = Neo4jGraph(url=neo4j_uri, username=neo4j_username, password=neo4j_password)
        # Connection success
    except Exception as e:
        print(f"❌ Init Error: {e}")
else:
    print("❌ Missing environment variables. Check .env file.")


# ==========================================
# 2. TOOL DEFINITION
# ==========================================

@tool
def get_flight_details(flight_code: str) -> dict:
    """
    Retrieves ALL available data for a flight code (e.g., 'LX 15', 'UA 9715').
    """
    if not graph:
        return {"error": "No database connection."}

    # 1. Input Cleaning
    clean_input = flight_code
    if "{" in flight_code and "}" in flight_code:
        try:
            data = json.loads(flight_code)
            if isinstance(data, dict):
                clean_input = list(data.values())[0]
        except:
            pass

    # 2. Normalization
    code_clean = str(clean_input).replace(" ", "").replace('"', '').upper()

    # 3. CYPHER QUERY
    cypher = """
    OPTIONAL MATCH (f_direct:Flight {flightNumber: $code})
    OPTIONAL MATCH (fd:FlightDesignator {code: $code})-[:ALIASES]->(f_aliased:Flight)

    WITH coalesce(f_direct, f_aliased) AS flight, 
         coalesce(fd, f_direct) AS input_node,
         CASE WHEN fd IS NOT NULL THEN true ELSE false END AS is_codeshare

    WHERE flight IS NOT NULL

    MATCH (op_airline:Airline)-[:OPERATES]->(flight)
    OPTIONAL MATCH (mkt_airline:Airline)-[:OPERATES]->(input_node)
    WHERE is_codeshare = true

    OPTIONAL MATCH (flight)-[:SERVES]->(route:Route)
    OPTIONAL MATCH (route)-[:ORIGIN]->(orig_ap:Airport)-[:LOCATED_IN]->(orig_c:Country)
    OPTIONAL MATCH (route)-[:DESTINATION]->(dest_ap:Airport)-[:LOCATED_IN]->(dest_c:Country)

    OPTIONAL MATCH (flight)-[:PLANNED_CONFIG]->(conf:AircraftConfig)-[:OF_TYPE]->(type:AircraftType)
    OPTIONAL MATCH (flight)-[:PLANNED_TERMINAL]->(term:Terminal)
    OPTIONAL MATCH (flight)-[:PLANNED_IN_SEASON]->(season:Season)

    RETURN 
        input_node.code AS requested_code,
        CASE WHEN is_codeshare THEN 'Marketing Code' ELSE 'Operating Flight' END AS code_type,
        flight.flightNumber AS operating_flight_number,
        op_airline.name AS operating_airline,
        mkt_airline.name AS marketing_airline,
        route.name AS route_code,
        orig_ap.name AS origin_airport,
        orig_c.name AS origin_country,
        dest_ap.name AS destination_airport,
        dest_c.name AS destination_country,
        type.name AS aircraft_type,
        conf.code AS aircraft_config_code,
        term.name AS terminal,
        season.name AS season
    LIMIT 1
    """

    try:
        result = graph.query(cypher, params={"code": code_clean})
        if result and len(result) > 0:
            return {k: v for k, v in result[0].items() if v is not None}
        else:
            return {"message": f"Flight {code_clean} not found in graph."}
    except Exception as e:
        return {"error": str(e)}


# ==========================================
# 3. GLOBAL AGENT SETUP
# ==========================================
agent_executor = None

if llm and graph:
    tools = [get_flight_details]

    prompt_template = """
You are a precise data retrieval assistant for Swissport. 
You answer questions ONLY using the information returned by your tools.

CRITICAL RULES:
1. Do NOT use outside knowledge. If the tool says "Not found", say "I have no information on that flight".
2. Do NOT invent flight routes, times, or aircraft.
3. When using the tool, provide ONLY the flight code as the input (e.g., "LX15"). Do not use JSON formatting.

TOOLS:
{tools}

FORMAT:
Question: the input question
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action (simple text, no JSON)
Observation: the result of the action
... (repeat Thought/Action/Observation if needed)
Final Answer: the final answer based ONLY on the Observation.

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
    agent_prompt = PromptTemplate.from_template(prompt_template)

    try:
        agent = create_react_agent(llm, tools, agent_prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    except Exception as e:
        print(f"❌ Error creating agent: {e}")


# ==========================================
# 4. MAIN EXECUTION
# ==========================================
def main():
    if agent_executor:
        print("✅ Agent Ready. Type 'quit' to exit.")
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() in ["quit", "exit"]:
                break
            try:
                # Add tool_code block before execution to reflect factual fetching
                # Note: This is simulated here as the real tool call happens inside the agent executor
                response = agent_executor.invoke({"input": user_input})
                print(f"Agent: {response['output']}")
            except Exception as e:
                print(f"❌ Error: {e}")
                traceback.print_exc()
    else:
        print("System not ready.")


if __name__ == "__main__":
    main()