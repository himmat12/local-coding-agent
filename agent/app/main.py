from dotenv import load_dotenv
import os
from datetime import datetime
import sys
import threading
import time

import httpx    

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")


class LoadingAnimation:
    def __init__(self):
        self.is_loading = False
        self.thread = None
        
    def start(self, message="Processing"):
        self.is_loading = True
        self.thread = threading.Thread(target=self._animate, args=(message,))
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        self.is_loading = False
        if self.thread:
            self.thread.join()
        # Clear the loading line
        print("\r" + " " * 50 + "\r", end="", flush=True)
        
    def _animate(self, message):
        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while self.is_loading:
            print(f"\r{message} {spinner[i % len(spinner)]}", end="", flush=True)
            time.sleep(0.1)
            i += 1


def call_ollama(prompt: str) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    try:
        resp = httpx.post(url, json=payload, timeout=300) # time out after 5 minutes - for long running tasks
        resp.raise_for_status()
    except Exception as e:
        print(f"[System]: error calling ollama: {e}", file=sys.stderr)
        return ""

    data = resp.json()
      
    return data.get("response", "")


COMMANDS = {
    "help": {
        "description": "Display this help message",
        "usage": "help or --help or ?"
    },
    "history": {
        "description": "Show complete chat history with timestamps",
        "usage": "history or show history"
    },
    "clear": {
        "description": "Clear chat history and start fresh",
        "usage": "clear"
    },
    "status": {
        "description": "Show current session status",
        "usage": "status"
    },
    "exit": {
        "description": "Exit the agent",
        "usage": "exit or quit or Ctrl+D"
    }
}


def display_help():
    """Display available commands and usage"""
    print("\n" + "="*60)
    print("[System]: 📚 AVAILABLE COMMANDS")
    print("="*60)
    for cmd, info in COMMANDS.items():
        print(f"\n  {cmd.upper():12} - {info['description']}")
        print(f"  {'':12}   Usage: {info['usage']}")
    print("\n" + "="*60)
    print("[System]: Type your question or use a command above")
    print("="*60 + "\n")


def display_status(chat_history):
    """Display current session status"""
    print("\n" + "-"*60)
    print("[System]: Session Status")
    print("-"*60)
    print(f"  Model:          {OLLAMA_MODEL}")
    print(f"  Ollama Host:    {OLLAMA_HOST}")
    print(f"  Messages:       {len(chat_history)}")
    print(f"  Last Update:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60 + "\n")


def main():
    print("[System]: starting up...")
    print(f"[System]: OLLAMA_HOST={OLLAMA_HOST}, model={OLLAMA_MODEL}")

    loader = LoadingAnimation()
    
    initial_prompt = "Say 'hello from the agent container'."
    chat_history = []
     
    loader.start("Initializing agent")
    answer = call_ollama(initial_prompt)
    loader.stop()
    
    # Check if we have a TTY for interactive input
    if sys.stdin.isatty():
        print("[System]: Running in interactive mode")
        display_help()
        
        while True:
            try:
                prompt = input("Ask anything: ")
            except (EOFError, KeyboardInterrupt):
                print("\n[System]: Goodbye!")
                break

            if not prompt.strip():
                continue
            
            # Command: Help
            if prompt.strip().lower() in {"help", "--help", "?"}:
                display_help()
                continue
            
            # Command: History
            if prompt.strip().lower() in {"history", "show history"}:
                print("\n[Chat History]:")
                print("-"*60)
                for i, msg in enumerate(chat_history, 1):
                    print(f"\n  [{i}] {msg['role'].upper()}")
                    print(f"      Message: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
                    print(f"      Time: {msg['timestamp'].strftime('%H:%M:%S')}")
                print("\n" + "-"*60 + "\n")
                continue
            
            # Command: Clear
            if prompt.strip().lower() == "clear":
                chat_history = []
                print("[System]: Chat history cleared")
                continue
            
            # Command: Status
            if prompt.strip().lower() == "status":
                display_status(chat_history)
                continue
            
            # Command: Exit
            if prompt.strip().lower() in {"exit", "quit"}:
                print("[System]: Goodbye!")
                break

            # Regular message
            print("[You]:", prompt)
            chat_history.append({"role": "user", "content": prompt, "timestamp": datetime.now()})

            loader.start("Generating response")
            full_prompt = "\n".join([f"{msg['role']}: {msg['content']}: {msg['timestamp']}" for msg in chat_history])
            answer = call_ollama(full_prompt)
            loader.stop()
            
            chat_history.append({"role": "assistant", "content": answer, "timestamp": datetime.now()})
            print("[Agent]:", repr(answer))
    else:
        print("[System]: Running in non-interactive mode (no TTY)")
        print("[System]: To interact with the agent, run:")
        print("  docker compose exec agent bash")
        print("  python3 main.py")
        # Keep the container running for logs
        import time
        while True:
            time.sleep(1)
 

if __name__ == "__main__":
    main()