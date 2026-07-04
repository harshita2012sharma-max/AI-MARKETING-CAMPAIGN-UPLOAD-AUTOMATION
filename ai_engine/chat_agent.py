"""
ai_engine/chat_agent.py
Groq + LLaMA 3 chat agent with conversation memoryP.
Reads live DB data and answers natural language questions.
"""
import json
import logging
import requests
from config.settings import settings
from services.analytics_service import AnalyticsService
from services.campaign_service import CampaignService

logger = logging.getLogger("ai_engine.chat_agent")

SYSTEM_PROMPT = """You are AdPulse AI, an expert marketing analyst assistant.
You have access to real campaign data from Google Ads, Meta Ads, and Bing Ads.
Answer questions clearly and concisely. Always back your answers with numbers.
Keep responses under 150 words. Be direct and actionable."""


class ChatAgent:

    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.campaign_service  = CampaignService()
        self.memory: list[dict] = []   # conversation memory (last 10 turns)

    def _get_context(self) -> str:
        """Build a summary of current campaign data to inject into the prompt."""
        try:
            kpis      = self.analytics_service.get_dashboard_kpis(30)
            top_camps = self.analytics_service.get_top_campaigns(30)
            worst     = self.analytics_service.get_worst_campaigns(7)

            top_names   = [c["name"] for c in top_camps[:3]]
            worst_names = [c["name"] for c in worst[:3]]

            return f"""
Current AdPulse Data (last 30 days):
- Total Spend: ₹{kpis.get('total_spend', 0):,.2f}
- Total Revenue: ₹{kpis.get('total_revenue', 0):,.2f}
- Total Clicks: {kpis.get('total_clicks', 0):,}
- Total Conversions: {kpis.get('total_conversions', 0):,}
- Average ROI: {kpis.get('avg_roi', 0):.2f}x
- Average CTR: {kpis.get('avg_ctr', 0):.2f}%
- Top campaigns by ROI: {', '.join(top_names)}
- Campaigns needing attention: {', '.join(worst_names)}
"""
        except Exception as exc:
            logger.error("Failed to build context: %s", exc)
            return "Campaign data temporarily unavailable."

    def chat(self, user_message: str) -> str:
        """
        Send message to Groq LLaMA 3. Returns AI reply as string.
        Falls back to rule-based reply if Groq key is missing.
        """
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
            return self._fallback_response(user_message)

        context = self._get_context()

        # Build messages with memory (last 10 exchanges)
        messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}]
        messages += self.memory[-10:]
        messages.append({"role": "user", "content": user_message})

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": messages,
                    "max_tokens": settings.GROQ_MAX_TOKENS,
                    "temperature": 0.7,
                },
                timeout=15
            )
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"].strip()

            # Save to memory
            self.memory.append({"role": "user", "content": user_message})
            self.memory.append({"role": "assistant", "content": reply})
            if len(self.memory) > 20:
                self.memory = self.memory[-20:]

            return reply

        except Exception as exc:
            logger.error("Groq API error: %s", exc)
            return self._fallback_response(user_message)

    def _fallback_response(self, message: str) -> str:
        """Rule-based fallback when Groq key is not set."""
        msg = message.lower()
        try:
            kpis = self.analytics_service.get_dashboard_kpis(30)
            if any(w in msg for w in ["spend", "budget", "cost"]):
                return f"Total spend in last 30 days: ₹{kpis.get('total_spend', 0):,.2f} across all platforms."
            if any(w in msg for w in ["roi", "return"]):
                return f"Average ROI across all campaigns: {kpis.get('avg_roi', 0):.2f}x. Revenue: ₹{kpis.get('total_revenue', 0):,.2f}."
            if any(w in msg for w in ["click", "ctr"]):
                return f"Total clicks: {kpis.get('total_clicks', 0):,} | Average CTR: {kpis.get('avg_ctr', 0):.2f}%."
            if any(w in msg for w in ["conversion"]):
                return f"Total conversions in 30 days: {kpis.get('total_conversions', 0):,}."
            if any(w in msg for w in ["best", "top", "performing"]):
                top = self.analytics_service.get_top_campaigns(30)
                if top:
                    return f"Best performing campaign: {top[0]['name']} with ROI {top[0].get('avg_roi', 0):.2f}x."
            return "I can answer questions about spend, ROI, CTR, conversions, and campaign performance. Add your Groq API key for full AI chat."
        except Exception:
            return "Unable to retrieve data right now. Please try again."