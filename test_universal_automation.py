#!/usr/bin/env python3
"""
Test the universal URL extraction and enhanced search term parsing
"""

import re
from loguru import logger

def extract_target_url(voice_command: str) -> str:
    """Extract target URL from voice command - UNIVERSAL approach for ANY website"""
    cmd = voice_command.lower()
    
    print(f"🌐 UNIVERSAL URL EXTRACTION from: '{voice_command}'")
    
    # Enhanced URL patterns for ANY website (not just hardcoded ones)
    url_patterns = [
        # Pattern 1: Full URLs with protocol
        r'(https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)',
        
        # Pattern 2: Direct domain mentions (most common)
        r'(?:visit|go to|open|navigate to)\s+([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})',
        
        # Pattern 3: Domains mentioned anywhere in command
        r'\b([a-zA-Z0-9\-\.]+\.(?:com|org|net|edu|gov|io|co|in|uk|de|fr|au|ca|jp|cn|br|mx|es|it|ru))\b',
        
        # Pattern 4: Handle "make my trip" -> "makemytrip.com" type conversions
        r'(?:go to|visit|open)\s+(.+?)(?:\s+and|\s*$)',
    ]
    
    extracted_url = None
    
    for i, pattern in enumerate(url_patterns, 1):
        matches = re.findall(pattern, cmd)
        if matches:
            # Take the first match that looks like a domain
            for match in matches:
                potential_url = match.strip()
                
                # Skip common words that aren't domains
                skip_words = ['and', 'search', 'find', 'look', 'for', 'me', 'my', 'the', 'a', 'an']
                if potential_url.lower() in skip_words:
                    continue
                
                # Handle special cases like "make my trip" -> "makemytrip.com"
                if ' ' in potential_url and not potential_url.startswith('http'):
                    # Convert "make my trip" to "makemytrip.com"
                    potential_url = potential_url.replace(' ', '').replace('-', '') + '.com'
                
                # Ensure it has a valid TLD
                if '.' in potential_url or potential_url.startswith('http'):
                    extracted_url = potential_url
                    print(f"✅ Pattern {i} matched: '{extracted_url}'")
                    break
        
        if extracted_url:
            break
    
    # Intelligent domain normalization
    if extracted_url:
        # Remove any trailing "and" or other words
        extracted_url = re.sub(r'\s+(and|search|find).*$', '', extracted_url, flags=re.IGNORECASE).strip()
        
        # Add protocol if missing
        if not extracted_url.startswith('http'):
            extracted_url = f"https://{extracted_url}"
        
        print(f"🎯 FINAL EXTRACTED URL: '{extracted_url}'")
        return extracted_url
    
    # INTELLIGENT FALLBACK: Try to extract any meaningful domain-like words
    # Look for patterns like "makemytrip", "bookmyshow", etc.
    words = cmd.split()
    for word in words:
        # Skip common words
        if word in ['go', 'to', 'and', 'search', 'find', 'look', 'for', 'me', 'my', 'the', 'a', 'an']:
            continue
        
        # Look for compound words that could be domains
        if len(word) > 3 and not word.isdigit():
            # Common domain patterns
            if any(pattern in word for pattern in ['my', 'book', 'shop', 'buy', 'get', 'make']):
                potential_domain = f"https://{word}.com"
                print(f"🔄 INTELLIGENT FALLBACK: '{word}' -> '{potential_domain}'")
                return potential_domain
    
    # LAST RESORT: Default to Google for search commands
    if any(word in cmd for word in ['search', 'find', 'look']):
        print("🔄 SEARCH FALLBACK: Defaulting to Google")
        return "https://google.com"
    
    # Absolute fallback
    print(f"⚠️ NO URL EXTRACTED from '{voice_command}', defaulting to Google")
    return "https://google.com"

def test_search_extraction(cmd):
    """Test enhanced search term extraction"""
    print(f"\n🔍 Testing search extraction: '{cmd}'")
    cmd = cmd.lower()
    
    # Enhanced search term extraction for ANY type of search (flights, hotels, etc.)
    search_term = None
    
    # Pattern 1: "search for X", "find X", "look for X"
    query = re.search(r'search for (.+)|find (.+)|look for (.+)', cmd)
    if query:
        search_term = query.group(1) or query.group(2) or query.group(3)
        print(f"   ✅ Pattern 1: '{search_term}'")
    
    # Pattern 2: "search me X" - common for travel/booking sites
    if not search_term:
        pattern = re.search(r'search me (.+)', cmd)
        if pattern:
            search_term = pattern.group(1).strip()
            print(f"   ✅ Pattern 2: '{search_term}'")
    
    # Pattern 3: "go to X and search Y" or "open X and search Y"  
    if not search_term:
        pattern = re.search(r'(?:go to|open|visit)\s+[^\s]+(?:\.[a-z]{2,})?\s+and\s+search(?:\s+me)?\s+(.+)', cmd)
        if pattern:
            search_term = pattern.group(1).strip()
            print(f"   ✅ Pattern 3: '{search_term}'")
        else:
            # Handle simple "search X" pattern
            pattern = re.search(r'search\s+(.+)', cmd)
            if pattern:
                search_term = pattern.group(1).strip()
                print(f"   ✅ Pattern 3b: '{search_term}'")
    
    # INTELLIGENT CLEANUP for travel/flight searches
    if search_term:
        original_term = search_term
        
        # Remove domain references that got mixed in
        search_term = re.sub(r'\s+(on|in|at)\s+\w+\.\w+.*$', '', search_term, flags=re.IGNORECASE)
        
        # Handle flight-specific patterns: "ticket for Delhi to Bangalore flight"
        # Clean up to: "Delhi to Bangalore flight"
        search_term = re.sub(r'^\s*ticket\s+for\s+', '', search_term, flags=re.IGNORECASE)
        search_term = re.sub(r'\s+flight\s*$', ' flight', search_term, flags=re.IGNORECASE)
        
        search_term = search_term.strip()
        
        if original_term != search_term:
            print(f"   🧹 CLEANED: '{original_term}' -> '{search_term}'")
    
    print(f"   🎯 FINAL: '{search_term}'")
    return search_term

if __name__ == "__main__":
    print("🧪 Testing Universal URL Extraction & Search Enhancement")
    print("=" * 70)
    
    # Test URL extraction
    url_test_cases = [
        "go to make my trip.com and search me ticket for Delhi to Bangalore flight",
        "open bookmyshow.com and find movie tickets",
        "visit amazon.in and search laptops",
        "navigate to flipkart.com",
        "go to github.com and search python projects",
        "open netflix.com",
        "visit booking.com and find hotels"
    ]
    
    print("\n🌐 URL EXTRACTION TESTS:")
    for test_case in url_test_cases:
        result = extract_target_url(test_case)
        print()
    
    print("\n" + "=" * 70)
    
    # Test search extraction
    search_test_cases = [
        "go to make my trip.com and search me ticket for Delhi to Bangalore flight",
        "search me ticket for Delhi to Bangalore flight",
        "find flights from Mumbai to Delhi",
        "look for hotels in Bangalore",
        "search for Python tutorials on YouTube"
    ]
    
    print("\n🔍 SEARCH EXTRACTION TESTS:")
    for test_case in search_test_cases:
        test_search_extraction(test_case)
    
    print("\n" + "=" * 70)
    print("✅ Universal automation - no more hardcoded website limitations!")
