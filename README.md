# Claude Local Content Engine

Generate SEO-optimized local landing page content at scale using the Anthropic Claude API.

Built for multi-location businesses (restaurants, healthcare, retail, services) that need to generate unique, high-quality local pages across hundreds of locations — without templated content that hurts rankings.

## The Problem

Multi-location brands face a content scaling challenge: each location needs a unique local landing page with genuine local context, proper SEO optimization, structured data, and FAQ schema. Manually writing these pages doesn't scale. Generic templates with city-name swaps get flagged as thin content by search engines.

## The Solution

This engine uses Claude to generate genuinely localized content for each location — not just swapping city names into a template, but producing contextually aware content that references real neighborhoods, local landmarks, and area-specific messaging. It then evaluates each page using an LLM-as-judge pattern to score quality across 6 dimensions.

## Features

- **Single location generation** — Generate a complete local page with one command
- **Batch processing** — Process hundreds of locations from a JSON file
- **Quality evaluation** — LLM-as-judge scoring across 6 dimensions (local relevance, SEO, content quality, conversion potential, schema accuracy, uniqueness)
- **HTML rendering** — Outputs preview-ready HTML with embedded JSON-LD structured data
- **Structured data** — Generates valid LocalBusiness and FAQPage schema automatically
- **Session stats** — Track tokens used, generation time, and throughput

## Quick Start
```bash
cat > README.md << 'ENDOFREADME'
# Claude Local Content Engine

Generate SEO-optimized local landing page content at scale using the Anthropic Claude API.

Built for multi-location businesses (restaurants, healthcare, retail, services) that need to generate unique, high-quality local pages across hundreds of locations — without templated content that hurts rankings.

## The Problem

Multi-location brands face a content scaling challenge: each location needs a unique local landing page with genuine local context, proper SEO optimization, structured data, and FAQ schema. Manually writing these pages doesn't scale. Generic templates with city-name swaps get flagged as thin content by search engines.

## The Solution

This engine uses Claude to generate genuinely localized content for each location — not just swapping city names into a template, but producing contextually aware content that references real neighborhoods, local landmarks, and area-specific messaging. It then evaluates each page using an LLM-as-judge pattern to score quality across 6 dimensions.

## Features

- **Single location generation** — Generate a complete local page with one command
- **Batch processing** — Process hundreds of locations from a JSON file
- **Quality evaluation** — LLM-as-judge scoring across 6 dimensions (local relevance, SEO, content quality, conversion potential, schema accuracy, uniqueness)
- **HTML rendering** — Outputs preview-ready HTML with embedded JSON-LD structured data
- **Structured data** — Generates valid LocalBusiness and FAQPage schema automatically
- **Session stats** — Track tokens used, generation time, and throughput

## Quick Start
```bash
git clone https://github.com/holdenstirling/claude-local-content-engine.git
cd claude-local-content-engine
pip3 install -r requirements.txt
export ANTHROPIC_API_KEY='your-key-here'
python3 cli.py demo
```

## Usage

### Generate a single page
```bash
python3 cli.py generate \
  --business "Joe's Pizza" \
  --industry "Pizza Restaurant" \
  --city "Denver" \
  --state "CO" \
  --services "New York style pizza, calzones, catering, delivery" \
  --keywords "pizza Denver, best pizza downtown Denver" \
  --evaluate \
  --output output/denver
```

### Batch generate from a JSON file
```bash
python3 cli.py batch \
  --input examples/locations.json \
  --output output/ \
  --evaluate
```

### Use as a Python library
```python
from src.engine import LocalContentEngine, render_html

engine = LocalContentEngine(api_key="your-key")

result = engine.generate_content({
    "business_name": "Summit Physical Therapy",
    "industry": "Physical Therapy",
    "city": "Denver",
    "state": "CO",
    "services": "Sports rehab, post-surgical recovery, dry needling",
    "target_keywords": "physical therapy Denver CO"
})

print(result["content"]["meta"]["title"])

# Evaluate quality
evaluation = engine.evaluate_content(result["location"], result["content"])
print(f"Overall score: {evaluation['evaluation']['overall_score']}/10")

# Render to HTML with embedded schema
html = render_html(result["content"])
```

## Output Structure

Each generated page produces:
```json
{
  "meta": { "title": "...", "description": "...", "canonical_slug": "..." },
  "content": {
    "h1": "...",
    "intro_paragraph": "...",
    "services_section": { "heading": "...", "body": "..." },
    "local_section": { "heading": "...", "body": "..." },
    "why_choose_us": { "heading": "...", "reasons": ["..."] },
    "cta_section": { "heading": "...", "body": "...", "cta_text": "..." }
  },
  "faq": [{ "question": "...", "answer": "..." }],
  "structured_data": { "@context": "https://schema.org", "@type": "LocalBusiness", "..." },
  "internal_linking_suggestions": ["..."]
}
```

## Evaluation Dimensions

When `--evaluate` is enabled, each page is scored 1-10 on:

| Dimension | What It Measures |
|---|---|
| **Local Relevance** | Is content genuinely localized or generic with a city name swapped in? |
| **SEO Optimization** | Keyword usage, heading hierarchy, meta tag quality |
| **Content Quality** | Writing quality, engagement, absence of filler content |
| **Conversion Potential** | CTA clarity, value proposition, action-driving language |
| **Schema Accuracy** | Validity and completeness of JSON-LD structured data |
| **Uniqueness** | Would this content be sufficiently different across 100+ location pages? |

## Prompt Engineering Approach

The engine uses a structured prompting strategy:

1. **System prompt** establishes the AI as a local SEO specialist with specific quality guidelines (no keyword stuffing, genuine localization, humans-first writing)
2. **Generation prompt** uses a strict JSON schema to ensure consistent, parseable output across all locations. The schema mirrors real-world local landing page architecture used by enterprise brands
3. **Evaluation prompt** implements an LLM-as-judge pattern — a separate Claude call evaluates the generated content against defined quality dimensions, providing both scores and qualitative feedback
4. **Separation of concerns** — generation and evaluation use separate API calls so the evaluator isn't biased by having generated the content in the same context window

This approach mirrors how production evaluation pipelines work in enterprise AI deployments: generate, evaluate, iterate.

## Why This Exists

I built this to solve a problem I've seen across 50+ enterprise implementations at [Arc4](https://arc4.com): multi-location brands consistently struggle to generate local content that's both unique enough to rank and consistent enough to maintain brand standards. Most teams either hand-write pages (doesn't scale past 20 locations) or use basic templates (gets flagged as thin/duplicate content).

This engine demonstrates that LLMs can generate genuinely differentiated local content at scale — but only with proper prompt architecture, structured output schemas, and quality evaluation guardrails.

## License

MIT

## Author

**Holden Ottolini** — [LinkedIn](https://linkedin.com/in/holden-stirling-ottolini) | [GitHub](https://github.com/holdenstirling)

Solutions Architect and Co-Founder at Arc4. 10+ years helping enterprise brands scale digital presence across hundreds of locations.
