"""
Claude Local Content Engine - Core Module

Generates SEO-optimized local landing page content for multi-location businesses
using the Anthropic Claude API.

Author: Holden Ottolini (holdenstirling)
"""

import json
import time
from anthropic import Anthropic

SYSTEM_PROMPT = """You are an expert local SEO content strategist specializing in multi-location businesses. You generate high-quality, unique local landing page content that ranks well in local search results and converts visitors into customers.

Your content must:
- Be genuinely localized (reference real neighborhood context, not generic filler)
- Follow current SEO best practices for local landing pages
- Include proper heading hierarchy (H1, H2, H3)
- Be written for humans first, search engines second
- Avoid keyword stuffing while maintaining topical relevance
- Generate valid JSON-LD structured data (LocalBusiness schema)

You always respond in valid JSON format as specified in the user prompt."""

CONTENT_GENERATION_PROMPT = """Generate complete local landing page content for the following business location:

**Business Name:** {business_name}
**Industry:** {industry}
**City:** {city}
**State:** {state}
**Address:** {address}
**Phone:** {phone}
**Services/Products:** {services}
**Unique Selling Points:** {unique_selling_points}
**Target Keywords:** {target_keywords}

Generate a complete JSON response with this exact structure:
{{
  "meta": {{
    "title": "SEO-optimized page title (50-60 chars, include city + primary keyword)",
    "description": "Meta description (150-160 chars, include city, CTA, and value prop)",
    "canonical_slug": "url-friendly-slug-with-city"
  }},
  "content": {{
    "h1": "Primary heading (include city name naturally)",
    "intro_paragraph": "2-3 sentences establishing local presence and primary value prop",
    "services_section": {{
      "heading": "H2 heading for services section",
      "body": "2-3 paragraphs about services offered at this location, with local context"
    }},
    "local_section": {{
      "heading": "H2 heading referencing the specific area/neighborhood",
      "body": "2-3 paragraphs with genuine local context"
    }},
    "why_choose_us": {{
      "heading": "H2 heading for differentiation",
      "reasons": ["reason 1", "reason 2", "reason 3", "reason 4"]
    }},
    "cta_section": {{
      "heading": "Action-oriented H2",
      "body": "1-2 sentences driving action",
      "cta_text": "Button text"
    }}
  }},
  "faq": [
    {{"question": "FAQ 1", "answer": "Answer 1"}},
    {{"question": "FAQ 2", "answer": "Answer 2"}},
    {{"question": "FAQ 3", "answer": "Answer 3"}},
    {{"question": "FAQ 4", "answer": "Answer 4"}},
    {{"question": "FAQ 5", "answer": "Answer 5"}}
  ],
  "structured_data": {{
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "{business_name}",
    "address": {{
      "@type": "PostalAddress",
      "streetAddress": "{address}",
      "addressLocality": "{city}",
      "addressRegion": "{state}"
    }},
    "telephone": "{phone}",
    "description": "Brief business description for schema",
    "areaServed": ["list of areas served"]
  }},
  "internal_linking_suggestions": [
    "Suggested internal link 1",
    "Suggested internal link 2",
    "Suggested internal link 3"
  ]
}}

IMPORTANT: Return ONLY the JSON object. No markdown, no code fences, no explanation."""

EVALUATION_PROMPT = """You are an expert local SEO auditor. Evaluate the following local landing page content and score it across multiple dimensions.

**Business Context:**
- Business: {business_name}
- Location: {city}, {state}
- Industry: {industry}
- Target Keywords: {target_keywords}

**Generated Content:**
{content_json}

Score each dimension from 1-10 and provide specific feedback. Return ONLY valid JSON:
{{
  "scores": {{
    "local_relevance": {{"score": 0, "feedback": "assessment"}},
    "seo_optimization": {{"score": 0, "feedback": "assessment"}},
    "content_quality": {{"score": 0, "feedback": "assessment"}},
    "conversion_potential": {{"score": 0, "feedback": "assessment"}},
    "schema_accuracy": {{"score": 0, "feedback": "assessment"}},
    "uniqueness": {{"score": 0, "feedback": "assessment"}}
  }},
  "overall_score": 0,
  "top_improvements": ["improvement 1", "improvement 2", "improvement 3"]
}}

IMPORTANT: Return ONLY the JSON object. No markdown, no code fences, no explanation."""


class LocalContentEngine:
    """
    Generates and evaluates SEO-optimized local landing page content
    using the Anthropic Claude API.
    """

    def __init__(self, api_key, model="claude-sonnet-4-20250514"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.generation_stats = {
            "total_generated": 0,
            "total_tokens_used": 0,
            "avg_generation_time": 0,
            "total_time": 0,
        }

    def generate_content(self, location):
        required = ["business_name", "industry", "city", "state"]
        missing = [f for f in required if f not in location]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        defaults = {
            "address": "",
            "phone": "",
            "services": "General services",
            "unique_selling_points": "Quality service, local expertise",
            "target_keywords": f"{location['industry']} {location['city']}",
        }
        for key, default in defaults.items():
            location.setdefault(key, default)

        prompt = CONTENT_GENERATION_PROMPT.format(**location)
        start_time = time.time()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        elapsed = time.time() - start_time
        raw_text = response.content[0].text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            raw_text = raw_text.rsplit("```", 1)[0]

        try:
            content = json.loads(raw_text)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {e}", "raw_response": raw_text, "location": location}

        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        self._update_stats(elapsed, tokens_used)

        return {
            "location": location,
            "content": content,
            "metadata": {
                "model": self.model,
                "generation_time_seconds": round(elapsed, 2),
                "tokens_used": tokens_used,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }

    def evaluate_content(self, location, content):
        prompt = EVALUATION_PROMPT.format(
            business_name=location.get("business_name", ""),
            city=location.get("city", ""),
            state=location.get("state", ""),
            industry=location.get("industry", ""),
            target_keywords=location.get("target_keywords", ""),
            content_json=json.dumps(content, indent=2),
        )

        start_time = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        elapsed = time.time() - start_time

        raw_text = response.content[0].text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            raw_text = raw_text.rsplit("```", 1)[0]

        try:
            evaluation = json.loads(raw_text)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse evaluation: {e}", "raw_response": raw_text}

        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        self._update_stats(elapsed, tokens_used)

        return {
            "evaluation": evaluation,
            "metadata": {"model": self.model, "evaluation_time_seconds": round(elapsed, 2), "tokens_used": tokens_used},
        }

    def generate_batch(self, locations, evaluate=False):
        results = []
        total = len(locations)
        for i, location in enumerate(locations, 1):
            city = location.get("city", "Unknown")
            state = location.get("state", "")
            print(f"  [{i}/{total}] Generating content for {city}, {state}...")
            result = self.generate_content(location)
            if evaluate and "error" not in result:
                print(f"  [{i}/{total}] Evaluating content quality...")
                eval_result = self.evaluate_content(location, result["content"])
                result["evaluation"] = eval_result.get("evaluation")
            results.append(result)
            if i < total:
                time.sleep(1)
        return results

    def get_stats(self):
        return self.generation_stats.copy()

    def _update_stats(self, elapsed, tokens):
        self.generation_stats["total_generated"] += 1
        self.generation_stats["total_tokens_used"] += tokens
        self.generation_stats["total_time"] += elapsed
        count = self.generation_stats["total_generated"]
        self.generation_stats["avg_generation_time"] = round(self.generation_stats["total_time"] / count, 2)


def render_html(content):
    meta = content.get("meta", {})
    body = content.get("content", {})
    faq = content.get("faq", [])
    schema = content.get("structured_data", {})

    faq_html = ""
    faq_schema_items = []
    for item in faq:
        q = item.get("question", "")
        a = item.get("answer", "")
        faq_html += f'    <div class="faq-item"><h3>{q}</h3><p>{a}</p></div>\n'
        faq_schema_items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})

    faq_schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_schema_items}

    reasons_html = ""
    for r in body.get("why_choose_us", {}).get("reasons", []):
        reasons_html += f"      <li>{r}</li>\n"

    links_html = ""
    for link in content.get("internal_linking_suggestions", []):
        links_html += f"    <li>{link}</li>\n"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta.get('title', '')}</title>
  <meta name="description" content="{meta.get('description', '')}">
  <link rel="canonical" href="/{meta.get('canonical_slug', '')}">
  <script type="application/ld+json">
{json.dumps(schema, indent=2)}
  </script>
  <script type="application/ld+json">
{json.dumps(faq_schema, indent=2)}
  </script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; }}
    h1 {{ font-size: 2rem; margin-bottom: 1rem; color: #1a1a1a; }}
    h2 {{ font-size: 1.5rem; margin: 2rem 0 0.75rem; color: #2a2a2a; }}
    h3 {{ font-size: 1.1rem; margin: 1rem 0 0.5rem; }}
    p {{ margin-bottom: 1rem; }}
    ul {{ margin: 0.5rem 0 1rem 1.5rem; }}
    li {{ margin-bottom: 0.5rem; }}
    .cta {{ background: #2563eb; color: white; padding: 0.75rem 2rem; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; display: inline-block; margin-top: 0.5rem; text-decoration: none; }}
    .faq-item {{ border-bottom: 1px solid #eee; padding: 1rem 0; }}
    .meta-preview {{ background: #f8f9fa; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 2rem; font-size: 0.85rem; }}
    .meta-preview .title {{ color: #1a0dab; font-size: 1.1rem; }}
    .meta-preview .url {{ color: #006621; }}
    .meta-preview .desc {{ color: #545454; }}
  </style>
</head>
<body>
  <div class="meta-preview">
    <div class="title">{meta.get('title', '')}</div>
    <div class="url">example.com/{meta.get('canonical_slug', '')}</div>
    <div class="desc">{meta.get('description', '')}</div>
  </div>
  <h1>{body.get('h1', '')}</h1>
  <p>{body.get('intro_paragraph', '')}</p>
  <h2>{body.get('services_section', {}).get('heading', '')}</h2>
  <p>{body.get('services_section', {}).get('body', '')}</p>
  <h2>{body.get('local_section', {}).get('heading', '')}</h2>
  <p>{body.get('local_section', {}).get('body', '')}</p>
  <h2>{body.get('why_choose_us', {}).get('heading', '')}</h2>
  <ul>
{reasons_html}  </ul>
  <h2>{body.get('cta_section', {}).get('heading', '')}</h2>
  <p>{body.get('cta_section', {}).get('body', '')}</p>
  <a href="#contact" class="cta">{body.get('cta_section', {}).get('cta_text', 'Contact Us')}</a>
  <h2>Frequently Asked Questions</h2>
{faq_html}
</body>
</html>"""
