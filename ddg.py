from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchResults, Tool
from langchain.prompts import PromptTemplate

# Initialize the language model
llm = OpenAI(model="gpt-3.5-turbo", api_key="your_openai_api_key")

# Define the DuckDuckGo search tool
ddg_search = DuckDuckGoSearchResults()

# Define a simple tool to filter results to get only Amazon and Flipkart URLs
def filter_results(search_results):
    filtered_urls = []
    for result in search_results:
        if "amazon.in" in result['url'] or "flipkart.com" in result['url']:
            filtered_urls.append(result['url'])
    return filtered_urls

filter_tool = Tool.from_function(
    func=filter_results,
    name="FilterAmazonFlipkart",
    description="Filters search results to get only Amazon and Flipkart URLs"
)

# Combine tools into a toolkit
tools = [ddg_search, filter_tool]

# Define the prompt template
prompt_template = PromptTemplate.from_template(
    "Find and list the best purchase links for the product {product_name}."
)

# Initialize the agent
agent = initialize_agent(
    tools=tools,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    llm=llm,
    prompt_template=prompt_template,
    verbose=True
)

# Run the agent with your input
product_name = "Samsung Galaxy S22"
response = agent.run({"product_name": product_name})

print("Filtered URLs:", response)
