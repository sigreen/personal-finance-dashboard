#!/usr/bin/env python3
"""Test MCP server connection and tools."""
import asyncio
import json
import httpx
from httpx_sse import aconnect_sse

async def test_mcp_connection():
    """Test MCP server SSE connection."""
    print("Testing MCP Server Connection...")
    print("=" * 50)

    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8081/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return

    # Test 2: SSE connection
    print("\n2. Testing SSE endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            async with aconnect_sse(client, "GET", "http://localhost:8081/sse") as event_source:
                print("   ✓ SSE connection established")

                # Send initialize request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    }
                }

                # Get session endpoint from initial message
                print("   Waiting for session endpoint...")
                async for event in event_source.aiter_sse():
                    if event.event == "endpoint":
                        endpoint_data = json.loads(event.data)
                        session_endpoint = f"http://localhost:8081{endpoint_data['uri']}"
                        print(f"   ✓ Session endpoint: {session_endpoint}")

                        # Send initialize request via POST
                        print("\n3. Sending initialize request...")
                        async with httpx.AsyncClient() as post_client:
                            init_response = await post_client.post(
                                session_endpoint,
                                json=init_request,
                                headers={"Content-Type": "application/json"}
                            )
                            print(f"   Status: {init_response.status_code}")
                            if init_response.status_code == 202:
                                print("   ✓ Initialize request accepted")

                        # Wait for initialize response
                        print("\n4. Waiting for server response...")
                        response_count = 0
                        async for event in event_source.aiter_sse():
                            if event.event == "message":
                                response_count += 1
                                msg = json.loads(event.data)
                                print(f"   Message {response_count}: {msg.get('method', msg.get('result', 'unknown'))}")

                                if response_count >= 2:  # Got initialize response
                                    print("\n5. Requesting tools list...")
                                    list_tools_request = {
                                        "jsonrpc": "2.0",
                                        "id": 2,
                                        "method": "tools/list"
                                    }

                                    async with httpx.AsyncClient() as post_client:
                                        tools_response = await post_client.post(
                                            session_endpoint,
                                            json=list_tools_request,
                                            headers={"Content-Type": "application/json"}
                                        )
                                        print(f"   Status: {tools_response.status_code}")

                                    # Wait for tools list response
                                    async for event in event_source.aiter_sse():
                                        if event.event == "message":
                                            msg = json.loads(event.data)
                                            if msg.get("id") == 2:
                                                tools = msg.get("result", {}).get("tools", [])
                                                print(f"\n   ✓ Found {len(tools)} tools:")
                                                for tool in tools[:5]:  # Show first 5
                                                    print(f"     - {tool['name']}: {tool['description'][:60]}...")
                                                print("\n✅ MCP Server is working correctly!")
                                                return
                        break

    except httpx.ConnectError:
        print("   ✗ Cannot connect to server. Is it running?")
        print("   Run: ./scripts/start-mcp-server.sh")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
