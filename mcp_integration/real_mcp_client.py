"""
REAL MCP Client - Connects to Microsoft's Playwright MCP Server
This replaces our fake "EnhancedPlaywrightMCP" with actual MCP protocol communication
"""
import json
import subprocess
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class RealMCPResult:
    """Result from REAL MCP server communication"""
    ok: bool
    data: Dict[str, Any] | None = None
    error: str | None = None
    request_id: str | None = None


class RealMCPClient:
    """
    REAL MCP Client that communicates with Microsoft's Playwright MCP Server
    Uses JSON-RPC over stdio as per MCP specification
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.request_counter = 0
        
    async def start_mcp_server(self) -> bool:
        """Start the Microsoft Playwright MCP server"""
        try:
            # Check if Node.js is available
            node_check = subprocess.run(['node', '--version'], 
                                      capture_output=True, text=True)
            if node_check.returncode != 0:
                logger.error("❌ Node.js not found! MCP requires Node.js 18+")
                return False
            
            logger.info(f"✅ Node.js found: {node_check.stdout.strip()}")
            
            # Start the Microsoft Playwright MCP server (using local build)
            logger.info("🚀 Starting Microsoft Playwright MCP server...")
            mcp_path = "/Users/bhanu.joshi/Desktop/HeyQ/playwright-mcp/cli.js"
            
            self.process = subprocess.Popen([
                'node', mcp_path, 
                '--browser', 'chrome',      # Use Chrome browser
                '--caps', 'vision'          # Enable vision capabilities for navigation
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
               stderr=subprocess.PIPE, text=True, bufsize=0)
            
            # Wait a moment for server to start
            await asyncio.sleep(3)
            
            if self.process.poll() is None:
                logger.info("✅ Microsoft Playwright MCP server started successfully")
                
                # Perform MCP initialization handshake
                init_success = await self._initialize_mcp_session()
                if init_success:
                    logger.info("✅ MCP session initialized successfully")
                    return True
                else:
                    logger.error("❌ MCP session initialization failed")
                    return False
            else:
                stderr_output = self.process.stderr.read() if self.process.stderr else "Unknown error"
                logger.error(f"❌ MCP server failed to start: {stderr_output}")
                return False
                
        except FileNotFoundError as e:
            logger.error(f"❌ MCP server executable not found: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            return False
    
    async def _initialize_mcp_session(self) -> bool:
        """Initialize MCP session with proper handshake"""
        try:
            # Step 1: Send initialize request
            init_result = await self.send_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "HeyQ-AI-MCP-Client",
                    "version": "1.0.0"
                }
            })
            
            if not init_result.ok:
                logger.error(f"❌ MCP initialize failed: {init_result.error}")
                return False
            
            logger.info("✅ MCP initialize successful")
            
            # Step 2: Send initialized notification
            initialized_result = await self.send_mcp_notification("notifications/initialized", {})
            
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP initialization failed: {e}")
            return False
    
    async def send_mcp_notification(self, method: str, params: Dict[str, Any]) -> bool:
        """Send MCP notification (no response expected)"""
        if not self.process or self.process.poll() is not None:
            return False
        
        # Construct JSON-RPC notification (no id field)
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        try:
            # Send notification
            notification_json = json.dumps(notification) + '\n'
            logger.debug(f"📤 MCP Notification: {notification_json.strip()}")
            
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ MCP notification failed: {e}")
            return False
    
    async def send_mcp_request(self, method: str, params: Dict[str, Any]) -> RealMCPResult:
        """Send JSON-RPC request to MCP server"""
        if not self.process or self.process.poll() is not None:
            return RealMCPResult(
                ok=False, 
                error="MCP server not running"
            )
        
        self.request_counter += 1
        request_id = f"req_{self.request_counter}"
        
        # Construct JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": request_id
        }
        
        try:
            # Send request
            request_json = json.dumps(request) + '\n'
            logger.debug(f"📤 MCP Request: {request_json.strip()}")
            
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response (with timeout)
            response_line = await asyncio.wait_for(
                asyncio.to_thread(self.process.stdout.readline), 
                timeout=30.0
            )
            
            if not response_line:
                return RealMCPResult(
                    ok=False,
                    error="No response from MCP server",
                    request_id=request_id
                )
            
            # Parse JSON-RPC response
            response = json.loads(response_line.strip())
            logger.debug(f"📥 MCP Response: {response}")
            
            if "error" in response:
                return RealMCPResult(
                    ok=False,
                    error=response["error"].get("message", "Unknown MCP error"),
                    request_id=request_id
                )
            
            return RealMCPResult(
                ok=True,
                data=response.get("result", {}),
                request_id=request_id
            )
            
        except asyncio.TimeoutError:
            return RealMCPResult(
                ok=False,
                error="MCP request timeout",
                request_id=request_id
            )
        except json.JSONDecodeError as e:
            return RealMCPResult(
                ok=False,
                error=f"Invalid JSON response: {e}",
                request_id=request_id
            )
        except Exception as e:
            return RealMCPResult(
                ok=False,
                error=f"MCP communication error: {e}",
                request_id=request_id
            )
    
    async def playwright_navigate(self, url: str) -> RealMCPResult:
        """Navigate to URL using REAL MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "playwright_navigate",
            "arguments": {"url": url}
        })
    
    async def playwright_click(self, selector: str) -> RealMCPResult:
        """Click element using REAL MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "playwright_click", 
            "arguments": {"selector": selector}
        })
    
    async def playwright_fill(self, selector: str, text: str) -> RealMCPResult:
        """Fill input using REAL MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "playwright_fill",
            "arguments": {"selector": selector, "text": text}
        })
    
    async def playwright_screenshot(self, name: str = "screenshot") -> RealMCPResult:
        """Take screenshot using REAL MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "playwright_screenshot",
            "arguments": {"name": name}
        })
    
    async def list_tools(self) -> RealMCPResult:
        """List available MCP tools"""
        return await self.send_mcp_request("tools/list", {})
    
    async def close(self):
        """Shutdown MCP server"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("✅ MCP server shutdown complete")
            except subprocess.TimeoutExpired:
                self.process.kill()
                logger.warning("⚠️ MCP server force killed")
            except Exception as e:
                logger.error(f"❌ Error shutting down MCP server: {e}")
            finally:
                self.process = None


# Example usage for testing
async def test_real_mcp():
    """Test the REAL MCP integration"""
    client = RealMCPClient()
    
    # Start MCP server
    if not await client.start_mcp_server():
        logger.error("❌ Cannot test - MCP server failed to start")
        return False
    
    try:
        # Test basic functionality
        logger.info("🧪 Testing REAL MCP integration...")
        
        # List available tools
        tools_result = await client.list_tools()
        logger.info(f"Available tools: {tools_result.data}")
        
        # Navigate to a test page
        nav_result = await client.playwright_navigate("https://example.com")
        logger.info(f"Navigation result: {nav_result.ok} - {nav_result.error or 'Success'}")
        
        # Take screenshot
        screenshot_result = await client.playwright_screenshot("test_real_mcp")
        logger.info(f"Screenshot result: {screenshot_result.ok} - {screenshot_result.error or 'Success'}")
        
        return nav_result.ok
        
    finally:
        await client.close()


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_real_mcp())
    print(f"REAL MCP Test Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
