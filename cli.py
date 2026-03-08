#!/usr/bin/env python3
"""
Claude Local Content Engine - CLI

Usage:
    python3 cli.py demo
    python3 cli.py generate --business "Joe's Pizza" --industry "Pizza Restaurant" --city "Denver" --state "CO"
    python3 cli.py batch --input examples/locations.json --output results/ --evaluate

Author: Holden Ottolini (holdenstirling)
"""

import argparse
import json
import os
import sys

from src.engine import LocalContentEngine, render_html


def get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    return key


def cmd_generate(args):
    engine = LocalContentEngine(api_key=get_api_key(), model=args.model)
    location = {
        "business_name": args.business,
        "industry": args.industry,
        "city": args.city,
        "state": args.state,
        "address": args.address or "",
        "phone": args.phone or "",
        "services": args.services or "",
        "unique_selling_points": args.usp or "",
        "target_keywords": args.keywords or f"{args.industry} {args.city}",
    }

    print(f"\n  Generating local content for {args.business} in {args.city}, {args.state}...")
    print(f"   Model: {args.model}\n")

    result = engine.generate_content(location)

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    content = result["content"]
    meta = content.get("meta", {})

    print(f"  Content generated in {result['metadata']['generation_time_seconds']}s")
    print(f"   Tokens used: {result['metadata']['tokens_used']:,}\n")
    print(f"  Title: {meta.get('title', 'N/A')}")
    print(f"  Desc:  {meta.get('description', 'N/A')}")
    print(f"  Slug:  /{meta.get('canonical_slug', 'N/A')}")
    print(f"  H1:    {content.get('content', {}).get('h1', 'N/A')}")
    print(f"  FAQs:  {len(content.get('faq', []))} generated")

    if args.evaluate:
        print(f"\n  Evaluating content quality...")
        eval_result = engine.evaluate_content(location, content)
        if "error" not in eval_result:
            ev = eval_result["evaluation"]
            scores = ev.get("scores", {})
            print(f"\n  Quality Scores:")
            for dim, data in scores.items():
                label = dim.replace("_", " ").title()
                score = data.get("score", "?")
                print(f"     {label:.<25} {score}/10")
            print(f"\n     Overall: {ev.get('overall_score', 'N/A')}/10")
            result["evaluation"] = ev

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        json_path = args.output if args.output.endswith(".json") else f"{args.output}.json"
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)
        html_path = json_path.replace(".json", ".html")
        with open(html_path, "w") as f:
            f.write(render_html(result["content"]))
        print(f"\n  JSON saved to: {json_path}")
        print(f"  HTML saved to: {html_path}")


def cmd_batch(args):
    engine = LocalContentEngine(api_key=get_api_key(), model=args.model)
    with open(args.input, "r") as f:
        locations = json.load(f)

    print(f"\n  Batch generating content for {len(locations)} locations...")
    print(f"   Model: {args.model}")
    print(f"   Evaluate: {'Yes' if args.evaluate else 'No'}\n")

    results = engine.generate_batch(locations, evaluate=args.evaluate)

    output_dir = args.output or "output"
    os.makedirs(output_dir, exist_ok=True)

    for i, result in enumerate(results):
        if "error" in result:
            print(f"  Warning: Error for location {i+1}: {result['error']}")
            continue
        loc = result["location"]
        slug = f"{loc['city'].lower().replace(' ', '-')}-{loc['state'].lower()}"
        with open(os.path.join(output_dir, f"{slug}.json"), "w") as f:
            json.dump(result, f, indent=2)
        with open(os.path.join(output_dir, f"{slug}.html"), "w") as f:
            f.write(render_html(result["content"]))
        score_str = ""
        if "evaluation" in result and result["evaluation"]:
            score = result["evaluation"].get("overall_score", "N/A")
            score_str = f" | Quality Score: {score}/10"
        print(f"  Done: {loc['city']}, {loc['state']}{score_str}")

    stats = engine.get_stats()
    print(f"\n  Session Stats:")
    print(f"   Pages generated: {stats['total_generated']}")
    print(f"   Total tokens: {stats['total_tokens_used']:,}")
    print(f"   Avg generation time: {stats['avg_generation_time']}s")
    print(f"   Output directory: {output_dir}/")


def cmd_demo(args):
    engine = LocalContentEngine(api_key=get_api_key(), model=args.model)

    demo_locations = [
        {
            "business_name": "Summit Physical Therapy",
            "industry": "Physical Therapy",
            "city": "Denver",
            "state": "CO",
            "address": "1550 Blake Street, Suite 200",
            "phone": "(303) 555-0142",
            "services": "Sports rehabilitation, post-surgical recovery, chronic pain management, dry needling, manual therapy",
            "unique_selling_points": "Same-day appointments, in-network with all major insurers, former pro sports team therapists on staff",
            "target_keywords": "physical therapy Denver, sports rehab Denver CO, physical therapist near me",
        },
        {
            "business_name": "Summit Physical Therapy",
            "industry": "Physical Therapy",
            "city": "Boulder",
            "state": "CO",
            "address": "2025 Pearl Street",
            "phone": "(303) 555-0198",
            "services": "Sports rehabilitation, post-surgical recovery, chronic pain management, dry needling, manual therapy",
            "unique_selling_points": "Trail running injury specialists, same-day appointments, in-network with all major insurers",
            "target_keywords": "physical therapy Boulder, sports rehab Boulder CO, physical therapist near me",
        },
    ]

    print("\n" + "=" * 60)
    print("  CLAUDE LOCAL CONTENT ENGINE - DEMO")
    print("=" * 60)
    print(f"\n  Generating local pages for 'Summit Physical Therapy'")
    print(f"  across {len(demo_locations)} locations with quality evaluation.\n")

    results = engine.generate_batch(demo_locations, evaluate=True)

    for result in results:
        if "error" in result:
            print(f"\n  Error: {result['error']}")
            continue

        loc = result["location"]
        content = result["content"]
        meta = content.get("meta", {})

        print(f"\n{'=' * 60}")
        print(f"  {loc['city']}, {loc['state']}")
        print(f"{'=' * 60}")
        print(f"\n  Title:  {meta.get('title', 'N/A')}")
        print(f"  Desc:   {meta.get('description', 'N/A')}")
        print(f"  Slug:   /{meta.get('canonical_slug', 'N/A')}")
        print(f"  H1:     {content.get('content', {}).get('h1', 'N/A')}")
        print(f"  FAQs:   {len(content.get('faq', []))} generated")

        if "evaluation" in result and result["evaluation"]:
            ev = result["evaluation"]
            scores = ev.get("scores", {})
            print(f"\n  Quality Evaluation:")
            for dim, data in scores.items():
                label = dim.replace("_", " ").title()
                score = data.get("score", "?")
                bar = "=" * score + "-" * (10 - score)
                print(f"     {label:.<25} [{bar}] {score}/10")
            overall = int(round(overall))
            print(f"\n     {'Overall Score':.<25} [{'=' * overall}{'-' * (10 - overall)}] {overall}/10")
            improvements = ev.get("top_improvements", [])
            if improvements:
                print(f"\n  Top Improvements:")
                for imp in improvements:
                    print(f"     -> {imp}")

    os.makedirs("demo_output", exist_ok=True)
    for result in results:
        if "error" not in result:
            loc = result["location"]
            slug = f"{loc['city'].lower()}-{loc['state'].lower()}"
            with open(f"demo_output/{slug}.json", "w") as f:
                json.dump(result, f, indent=2)
            with open(f"demo_output/{slug}.html", "w") as f:
                f.write(render_html(result["content"]))

    stats = engine.get_stats()
    print(f"\n{'=' * 60}")
    print(f"  Session Stats")
    print(f"{'=' * 60}")
    print(f"  Pages generated:     {stats['total_generated']}")
    print(f"  Total tokens used:   {stats['total_tokens_used']:,}")
    print(f"  Avg generation time: {stats['avg_generation_time']}s")
    print(f"\n  Output saved to: demo_output/")
    print(f"  Open the .html files in a browser to preview!\n")


def main():
    parser = argparse.ArgumentParser(
        description="Claude Local Content Engine - Generate SEO-optimized local landing pages at scale",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model to use")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    gen = subparsers.add_parser("generate", help="Generate content for a single location")
    gen.add_argument("--business", required=True, help="Business name")
    gen.add_argument("--industry", required=True, help="Industry/category")
    gen.add_argument("--city", required=True, help="City name")
    gen.add_argument("--state", required=True, help="State abbreviation")
    gen.add_argument("--address", help="Street address")
    gen.add_argument("--phone", help="Phone number")
    gen.add_argument("--services", help="Comma-separated list of services")
    gen.add_argument("--usp", help="Unique selling points")
    gen.add_argument("--keywords", help="Target keywords")
    gen.add_argument("--evaluate", action="store_true", help="Run quality evaluation")
    gen.add_argument("--output", help="Output file path (without extension)")

    batch = subparsers.add_parser("batch", help="Batch generate from JSON file")
    batch.add_argument("--input", required=True, help="Input JSON file")
    batch.add_argument("--output", help="Output directory")
    batch.add_argument("--evaluate", action="store_true", help="Run quality evaluation")

    subparsers.add_parser("demo", help="Run demo with sample locations")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "batch":
        cmd_batch(args)
    elif args.command == "demo":
        cmd_demo(args)


if __name__ == "__main__":
    main()
