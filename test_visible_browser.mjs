#!/usr/bin/env node

// Direct test of Playwright browser to see if it opens visibly
import { chromium } from 'playwright';

console.log('🚀 Starting visible browser test...');

const browser = await chromium.launch({ 
    headless: false,  // Force visible browser
    slowMo: 1000     // Slow down actions so we can see them
});

console.log('✅ Browser launched');

const context = await browser.newContext();
const page = await context.newPage();

console.log('📍 Navigating to YouTube...');
await page.goto('https://youtube.com');

console.log('✅ Navigation complete - browser should be visible!');
console.log('⏰ Keeping browser open for 10 seconds...');

// Keep browser open for 10 seconds so you can see it
await new Promise(resolve => setTimeout(resolve, 10000));

await browser.close();
console.log('🔚 Browser closed');
