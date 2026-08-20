import asyncio
import os
from dotenv import load_dotenv
#from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

async def run_memory_chat():
    """Run a memory chat using MCPagent build in conversation memorywith the MCPClient"""
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

    # Create MCPClient with Airbnb configuration
    client = MCPClient.from_config_file(
        os.path.join(os.path.dirname(__file__), "browser_mcp.json")
    )

    # Create LLM - you can choose between different models

    llm = ChatGroq(model="qwen/qwen3-32b")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30, memory_enabled=True)

    print ("\n====Interactive MCP Chat =====")
    print ("Enter 'exit' or 'quit ' end the chat. ")
    print ("Enter 'clear' to clear the conversation memory.")
    print ("Enter 'history' to see the conversation history.")
    print ("=========================")

    try:
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['exit', 'quit']:
                print ("\nThank you for using the MCP Chat! Goodbye!")
                break

            elif user_input.lower() == 'clear':
                agent.memory.clear()
                print ("\nConversation memory cleared.")

            elif user_input.lower() == 'history':
                print ("\nConversation history:")
                for message in agent.memory.messages:
                    print (f"{message['role']}: {message['content']}")
                    continue
            else:
                result = await agent.run(user_input, max_steps=30)
                print (f"\nResult: {result}")
                continue
        
            print("\nAssistant: ", end="", flush=True)  
            print(result.response)  

            try:
                result = await agent.run(user_input, max_steps=30)
                print(result.response)

            except Exception as e:
                print (f"\nError: {e}")
         
    finally:
        # Ensure we clean up resources properly
        if client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(run_memory_chat())
