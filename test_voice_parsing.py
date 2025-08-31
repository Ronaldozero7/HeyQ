#!/usr/bin/env python3
"""
Quick test script to validate voice command parsing logic
"""

import re

def test_search_parsing(cmd):
    """Test the enhanced search term extraction logic"""
    print(f"\n🧪 Testing command: '{cmd}'")
    cmd = cmd.lower()
    
    # Enhanced search term extraction with multiple patterns
    search_term = None
    
    # Pattern 1: "search for X", "find X", "look for X"
    query = re.search(r'search for (.+)|find (.+)|look for (.+)', cmd)
    if query:
        search_term = query.group(1) or query.group(2) or query.group(3)
        print(f"   ✅ Pattern 1 matched: '{search_term}'")
    
    # Pattern 2: "search X" (without "for"), "go to Y and search X"  
    if not search_term:
        # Handle "go to X and search Y" or "open X and search Y"
        pattern = re.search(r'(?:go to|open|visit)\s+[^\s]+\s+and\s+search\s+(.+)', cmd)
        if pattern:
            search_term = pattern.group(1).strip()
            print(f"   ✅ Pattern 2a matched: '{search_term}'")
        else:
            # Handle simple "search X" pattern
            pattern = re.search(r'search\s+(.+)', cmd)
            if pattern:
                search_term = pattern.group(1).strip()
                print(f"   ✅ Pattern 2b matched: '{search_term}'")
    
    # Pattern 3: Extract everything after "find" or "look"
    if not search_term:
        if 'find ' in cmd:
            search_term = cmd.split('find ', 1)[1].strip()
            print(f"   ✅ Pattern 3a matched: '{search_term}'")
        elif 'look ' in cmd:
            search_term = cmd.split('look ', 1)[1].strip()
            print(f"   ✅ Pattern 3b matched: '{search_term}'")
    
    # Clean up search term (remove common stop words at the end)
    if search_term:
        original = search_term
        # Remove trailing words like "on youtube", "in google", etc.
        search_term = re.sub(r'\s+(on|in|at)\s+\w+\.\w+.*$', '', search_term, flags=re.IGNORECASE)
        search_term = search_term.strip()
        if original != search_term:
            print(f"   🧹 Cleaned: '{original}' -> '{search_term}'")
    
    # Final fallback with better default
    if not search_term or len(search_term.strip()) == 0:
        # Try to extract any meaningful content after removing navigation words
        cleaned_cmd = re.sub(r'(go to|open|visit|navigate to)\s+[^\s]+\s*(and\s*)?', '', cmd, flags=re.IGNORECASE)
        cleaned_cmd = re.sub(r'\b(search|find|look)\s*', '', cleaned_cmd, flags=re.IGNORECASE).strip()
        search_term = cleaned_cmd if cleaned_cmd else "trending"
        print(f"   🔄 Fallback applied: '{search_term}'")
    
    print(f"   🎯 FINAL RESULT: '{search_term}'")
    return search_term

if __name__ == "__main__":
    print("🧪 Testing Voice Command Parsing Logic")
    print("=" * 50)
    
    test_cases = [
        "open youtube.com search Britney Spear songs",
        "go to youtube.com and search Britney Spears",
        "search for Python tutorials",
        "search Python tutorials",
        "find Taylor Swift music",
        "look for cooking videos",
        "go to google.com and search machine learning",
        "open netflix.com search comedy movies",
        "search",  # Edge case
        "find",    # Edge case
    ]
    
    for test_case in test_cases:
        result = test_search_parsing(test_case)
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary: Enhanced parsing should correctly extract search terms!")
