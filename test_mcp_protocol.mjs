#!/usr/bin/env node

// Direct MCP protocol test
import { spawn } from 'child_process';

console.log('🧪 Testing MCP server directly...');

const mcpProcess = spawn('node', ['/Users/bhanu.joshi/Desktop/HeyQ/playwright-mcp/cli.js', '--browser', 'chrome'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

// MCP initialization request
const initRequest = {
  jsonrpc: "2.0",
  method: "initialize", 
  params: {
    protocolVersion: "2024-11-05",
    capabilities: { roots: { listChanged: true }, sampling: {} },
    clientInfo: { name: "Direct-Test", version: "1.0.0" }
  },
  id: "req_1"
};

console.log('📤 Sending MCP initialize...');
mcpProcess.stdin.write(JSON.stringify(initRequest) + '\n');

mcpProcess.stdout.on('data', (data) => {
  console.log('📥 MCP Response:', data.toString());
});

mcpProcess.stderr.on('data', (data) => {
  console.log('❌ MCP Error:', data.toString());
});

setTimeout(() => {
  console.log('🔚 Test complete');
  mcpProcess.kill();
}, 5000);
