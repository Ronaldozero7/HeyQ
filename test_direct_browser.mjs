#!/usr/bin/env node

// Test browser opening with explicit configuration
import { execSync } from 'child_process';

console.log('🧪 Testing browser opening directly...');

// First, let's see if Chrome opens at all
try {
  console.log('🚀 Opening Chrome directly to YouTube...');
  execSync('open -a "Google Chrome" https://youtube.com', { timeout: 5000 });
  console.log('✅ Chrome should be opening YouTube now!');
} catch (error) {
  console.log('❌ Chrome direct open failed:', error.message);
}

console.log('Test complete - did you see Chrome open?');
