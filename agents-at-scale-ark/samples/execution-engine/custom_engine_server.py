
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys

# ==============================================================================
# PROTOCOL DEFINITION (Based on ark/internal/genai/execution_engine.go)
# ==============================================================================
#
# REQUEST JSON:
# {
#   "agent": { 
#       "name": "...", "namespace": "...", "prompt": "...", 
#       "model": { "name": "...", "type": "...", "config": {...} } 
#   },
#   "userInput": { "role": "user", "content": "..." },
#   "history": [ { "role": "...", "content": "..." } ],
#   "tools": [ { "name": "...", "description": "..." } ]
# }
#
# RESPONSE JSON:
# {
#   "messages": [ { "role": "assistant", "content": "..." } ],
#   "error": "", 
#   "token_usage": { "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0 }
# }
# ==============================================================================

class ArkProtocolHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/execute':
            try:
                # 1. READ REQUEST
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request = json.loads(post_data)

                # 2. PARSE ARK CONTEXT
                agent_name = request.get('agent', {}).get('name', 'unknown')
                user_content = request.get('userInput', {}).get('content', '')
                history = request.get('history', [])
                tools = request.get('tools', [])
                
                print(f"\n[Engine] 📨 Received Request for Agent: '{agent_name}'")
                print(f"  - User Input: {user_content}")
                print(f"  - History Depth: {len(history)} messages")
                print(f"  - Available Tools: {len(tools)} found")

                # 3. EXECUTE LOGIC (The "Brain" of your ADK)
                # Here we simulate some processing. In a real ADK, you would:
                # - Call LangChain / AutoGen / LlamaIndex
                # - Check a vector database
                # - Run complex Python code
                
                reply_text = (
                    f"✅ **Execution Engine Success**\n\n"
                    f"I am a custom Python engine compliant with Ark Protocol.\n"
                    f"- **Agent**: `{agent_name}`\n"
                    f"- **Received**: \"{user_content}\"\n"
                    f"- **Context**: I see {len(history)} previous messages.\n"
                )

                # 4. CONSTRUCT RESPONSE (Strictly typed)
                response = {
                    "messages": [
                        {
                            "role": "assistant",
                            "content": reply_text
                        }
                    ],
                    "token_usage": {
                        "prompt_tokens": len(user_content),
                        "completion_tokens": len(reply_text),
                        "total_tokens": len(user_content) + len(reply_text)
                    }
                }

                # 5. SEND RESPONSE
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                print(f"[Engine] 📤 Sent Response (Length: {len(reply_text)})")

            except Exception as e:
                print(f"Error processing request: {e}")
                error_response = {"error": str(e), "messages": []}
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(port=8090):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ArkProtocolHandler)
    print(f"🚀 Ark Custom Execution Engine started on port {port}")
    print("Waiting for traffic from Ark Controller...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()
        sys.exit(0)

if __name__ == '__main__':
    run()
