import jsonschema
from dotenv import load_dotenv
import os
from datetime import datetime
import sys
import json
import time
import httpx
from tools.arithmetic_tools import TOOLS  
from SCHEMAS import AGENT_SCHEMA, TOOL_SPECS

load_dotenv()
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


def ollama_generate(prompt: str, is_json_response: bool = True):
    url = f"{OLLAMA_HOST}/api/generate"
    print(f"\n[ollama_generate]: Sending request to {url}\n")
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }

    if is_json_response:
        payload["format"] = AGENT_SCHEMA

    try:
        response = httpx.post(url, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()

        response_text = data.get("response", "{}")
        
        if is_json_response:
            try:
                return json.loads(response_text)
            except Exception as e:
                return {"message": response_text, "error": f"{e}"}
        
        return response_text

    except Exception as e:
        print(f"[Exception]: Error calling ollama: {e}", file=  sys.stderr)
        return ""
        
def create_message(role: str, content: str ) -> dict:
    return {
        "role": role,
        "content": content,
        "timestamp": f"{datetime.now()}"
    }
    
system_message = create_message(
    "system",
    """
You are a helpful assistant assisting the user with any kind of query.

You must always return valid JSON matching the provided schema.

If the user's request requires arithmetic computation, operate in a Thought -> Action -> Observation loop:
1. Write short reasoning in "thought".
2. If a calculation is needed, set action="tool_call".
3. Choose the correct tool_name.
4. Provide arguments using the exact parameter names required by the tool.
5. After an observation is provided, reassess the user request.
6. Repeat only if another tool call is needed.
7. When the answer is ready, set action="final", tool_name=null, arguments={}, and put the final user-facing answer in "message".

If the user's request does NOT require arithmetic computation:
- Do NOT call any tool.
- Set action="final".
- Set tool_name=null.
- Set arguments={}
- Put the user-facing response in "message".

Available tools and exact signatures:
- add(x: number, y: number)
- subtract(x: number, y: number)
- multiply(x: number, y: number)
- divide(x: number, y: number)
- mod(x: number, y: number)
- get_x_percentage_of_y(x: number, y: number)
- pi()

Important rules:
- Use the exact argument names x and y for tools that require inputs.
- Use {} for pi().
- Do not invent argument names like a, b, number, factor, arg1, arg2, math_type, or op.
- Do not invent tool results.
- Keep "thought" short and task-focused.
"""
)

conversation_context = [system_message]

def parse_conversation_context() -> str:
    lines = []

    for message in conversation_context:
        lines.append(f"{message['role'].upper()}: {message['content']}\n")

    return "\n".join(lines)


def validate_tool_args(tool_name: str, args: dict) -> tuple[bool, str]:
    spec = TOOL_SPECS.get(tool_name)
    if not spec:
        return False, f"Unknown tool: {tool_name}"

    try:
        jsonschema.validate(instance=args, schema=spec)
        return True, "Valid"
    except jsonschema.ValidationError as e:
        return False, e.message

def run_planning_agent(user_prompt: str):
    planning_prompt = f"""
    You are a planning agent that creates a step-by-step plan to answer the user's question.  
    Your response should be a JSON object with a "plan" field that contains an array of steps. 
    Each step should be a string describing a single action or thought process that leads towards 
    answering the user's question. The plan should be detailed and cover all necessary steps to arrive at the final answer. 
    The user's question is: "{user_prompt}".
    """
    return ollama_generate(planning_prompt)


def run_agent(user_prompt: str, max_steps: int = 5):
    plan = run_planning_agent(user_prompt)
    conversation_context.append(create_message("plan", plan))
    print(f"\n[plan]: Generated plan:\n{plan}\n")
    
    conversation_context.append(create_message("[plan]", plan))

    for step in range(max_steps):
        context = parse_conversation_context()
        llm_response = ollama_generate(context)

        if not isinstance(llm_response, dict):
            final_message = str(llm_response)
            conversation_context.append(create_message("assistant", final_message))
            return final_message

        thought = llm_response.get("thought", "")
        action = llm_response.get("action")
        tool_name = llm_response.get("tool_name")
        arguments = llm_response.get("arguments", {})
        message = llm_response.get("message", "")

        print(f"\n[thought]: {thought}")
        print(f"[llm raw]: {llm_response}")

        if action == "final":
            conversation_context.append(create_message("assistant", message))
            return message

        elif action == "tool_call":
            is_valid, validation_msg = validate_tool_args(tool_name, arguments)

            if not is_valid:
                tool_call_respose = f"Tool '{tool_name}' validation failed: {validation_msg}"
                print(f"[tool_call]: {tool_call_respose}")
                conversation_context.append(create_message("observation", tool_call_respose))
                continue

            try:
                tool_result = TOOLS[tool_name](**arguments)
                tool_call_respose = f"Tool '{tool_name}' with arguments {arguments} returned: {tool_result}"
            except Exception as e:
                tool_call_respose = f"Tool '{tool_name}' failed with error: {str(e)}"

            print(f"[tool_call]: {tool_call_respose}")
            conversation_context.append(create_message("tool_call", tool_call_respose))
            continue

        else:
            observation = f"Unexpected action: {action}"
            print(f"[observation]: {observation}")
            conversation_context.append(create_message("observation", observation))
            continue

    final_message = "Max agent steps reached without a final answer."
    conversation_context.append(create_message("assistant", final_message))
    return final_message

def main():
    print("This is a playground for testing code snippets and ideas.")

    user_input = lambda: input("Enter a prompt for the model (or 'exit' to quit): ")
    
    while True:
        user_prompt = user_input() 
        isJsonResponse = True

        if user_prompt.lower() == "exit":
            print("Exiting...")
            break
        
        if user_prompt.lower() == "json":
            isJsonResponse = True
            print("LLM response set to JSON.")
            user_prompt = user_input()
        
        if user_prompt.lower() == "!json":
            isJsonResponse = False
            print("LLM response set to TEXT.")
            user_prompt = user_input()
        
        if user_prompt.lower() == "history":
            print(f"\nHISTORY:\n\n[conversation context]:\n{conversation_context}")
            print(parse_conversation_context())
            
            user_prompt = user_input()
        
        print(f"\n[user]: {user_prompt}")
        
        assistant_message = run_agent(user_prompt)

        print(f"\n[assistant]: {assistant_message}")


if __name__ == "__main__":
    main()