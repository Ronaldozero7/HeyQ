"""
Enhanced LLM Client for Voice-to-Intent Conversion
Supports OpenAI GPT and Anthropic Claude with fallback to regex parsing
"""
from __future__ import annotations
import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger
import openai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class LLMIntent:
    """Enhanced intent structure with LLM-generated details"""
    action: str
    site: Optional[str] = None
    item: Optional[str] = None
    qty: int = 1
    verify_price: bool = False
    confidence: float = 0.0
    reasoning: Optional[str] = None
    mcp_actions: Optional[List[Dict]] = None


class LLMClient:
    """Enhanced AI client for voice command understanding"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients with environment variables"""
        try:
            if openai_key := os.getenv('OPENAI_API_KEY'):
                # Simple OpenAI client initialization without extra parameters
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")
            
            if anthropic_key := os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic client initialized")
                
            if not self.openai_client and not self.anthropic_client:
                logger.warning("⚠️ No LLM API keys found - falling back to regex-only parsing")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize LLM clients: {e}")
            # Reset clients on error
            self.openai_client = None
            self.anthropic_client = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def parse_voice_intent(self, voice_text: str, context: Dict = None) -> LLMIntent:
        """Parse voice command using LLM with structured output"""
        
        # Try OpenAI first, then Anthropic, then fallback
        for provider in ["openai", "anthropic"]:
            try:
                if provider == "openai" and self.openai_client:
                    return self._parse_with_openai(voice_text, context)
                elif provider == "anthropic" and self.anthropic_client:
                    return self._parse_with_anthropic(voice_text, context)
            except Exception as e:
                logger.warning(f"❌ {provider.title()} parsing failed: {e}")
                continue
        
        # Fallback to regex-based parsing
        logger.info("🔄 Falling back to regex-based intent parsing")
        return self._fallback_regex_parse(voice_text)
    
    def _parse_with_openai(self, voice_text: str, context: Dict = None) -> LLMIntent:
        """Parse using OpenAI GPT with function calling"""
        
        system_prompt = """You are an expert voice command parser for test automation.
        Parse the user's voice command into structured automation intents.
        
        Available actions: navigate, login_only, add_to_cart, checkout, full_checkout_flow, search
        Supported sites: saucedemo, flipkart, amazon
        
        Always return valid JSON with action, site, item, qty, verify_price, confidence, reasoning."""
        
        user_prompt = f"""
        Voice command: "{voice_text}"
        Context: {context or {}}
        
        Parse this into automation intent JSON.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message.content)
        return LLMIntent(
            action=result.get('action', 'unknown'),
            site=result.get('site'),
            item=result.get('item'),
            qty=result.get('qty', 1),
            verify_price=result.get('verify_price', False),
            confidence=result.get('confidence', 0.8),
            reasoning=result.get('reasoning'),
            mcp_actions=result.get('mcp_actions')
        )
    
    def _parse_with_anthropic(self, voice_text: str, context: Dict = None) -> LLMIntent:
        """Parse using Anthropic Claude"""
        
        prompt = f"""Parse this voice command for test automation:

Voice: "{voice_text}"
Context: {context or {}}

Return JSON with:
- action: navigate|login_only|add_to_cart|checkout|full_checkout_flow|search
- site: saucedemo|flipkart|amazon (if mentioned)
- item: product name (if mentioned) 
- qty: quantity (default 1)
- verify_price: boolean
- confidence: 0.0-1.0
- reasoning: why you chose this interpretation

JSON:"""

        response = self.anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = json.loads(response.content[0].text)
        return LLMIntent(
            action=result.get('action', 'unknown'),
            site=result.get('site'),
            item=result.get('item'),
            qty=result.get('qty', 1),
            verify_price=result.get('verify_price', False),
            confidence=result.get('confidence', 0.7),
            reasoning=result.get('reasoning')
        )
    
    def _fallback_regex_parse(self, voice_text: str) -> LLMIntent:
        """Fallback to original regex-based parsing"""
        import re
        
        text = voice_text.lower().strip()
        
        # Login patterns
        if re.search(r"(?:open|go\s+to).*(?:login|log\s+in)(?!.*add.*cart)", text):
            return LLMIntent(action="login_only", confidence=0.9, reasoning="Regex: login pattern")
        
        # Add to cart patterns
        if re.search(r"\b(add|put|place)\s+.*\s+(?:to|into|in)\s+(?:cart|basket)", text):
            item_match = re.search(r"(?:add|put|place)\s+(?P<item>.+?)\s+(?:to|into|in)", text)
            item = item_match.group('item') if item_match else 'backpack'
            return LLMIntent(action="add_to_cart", item=item, confidence=0.8, reasoning="Regex: add to cart")
        
        # Site detection
        site = None
        if "saucedemo" in text:
            site = "saucedemo"
        elif "flipkart" in text:
            site = "flipkart"
        elif "amazon" in text:
            site = "amazon"
        
        return LLMIntent(
            action="navigate", 
            site=site, 
            confidence=0.6, 
            reasoning="Regex: fallback navigation"
        )

    def generate_mcp_actions(self, intent: LLMIntent, page_context: Dict = None) -> List[Dict]:
        """Generate MCP protocol actions for the given intent"""
        
        if not (self.openai_client or self.anthropic_client):
            return self._fallback_mcp_actions(intent)
        
        try:
            prompt = f"""Generate MCP protocol actions for this automation intent:

Intent: {intent.action}
Site: {intent.site}
Item: {intent.item}
Quantity: {intent.qty}
Page Context: {page_context or {}}

Return JSON array of MCP actions with format:
[
  {{"action": "navigate", "url": "https://example.com"}},
  {{"action": "fill", "selector": "#input", "text": "value"}},
  {{"action": "click", "selector": "#button"}}
]

Focus on {intent.site or 'saucedemo'} website structure.
JSON Array:"""

            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                return json.loads(response.choices[0].message.content).get('actions', [])
            
        except Exception as e:
            logger.warning(f"❌ MCP generation failed: {e}")
        
        return self._fallback_mcp_actions(intent)
    
    def _fallback_mcp_actions(self, intent: LLMIntent) -> List[Dict]:
        """Generate hardcoded MCP actions as fallback"""
        
        actions = []
        site_url = {
            "saucedemo": "https://www.saucedemo.com",
            "flipkart": "https://www.flipkart.com",
            "amazon": "https://www.amazon.com"
        }.get(intent.site, "https://www.saucedemo.com")
        
        if intent.action in ["navigate", "login_only", "full_checkout_flow"]:
            actions.append({"action": "navigate", "url": site_url})
        
        if intent.action in ["login_only", "full_checkout_flow"]:
            actions.extend([
                {"action": "fill", "selector": "#user-name", "text": "standard_user"},
                {"action": "fill", "selector": "#password", "text": "secret_sauce"},
                {"action": "click", "selector": "#login-button"}
            ])
        
        if intent.action in ["add_to_cart", "full_checkout_flow"] and intent.item:
            actions.append({
                "action": "click", 
                "selector": f"button[data-test*='add-to-cart']:has-text('{intent.item}')"
            })
        
        return actions


# Global instance
llm_client = LLMClient()
