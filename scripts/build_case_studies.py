
import os
import json
import yaml
from pathlib import Path

# This script builds static JSON files from the markdown case studies.

CASE_STUDIES_SRC_DIR = Path("case_studies")
OUTPUT_DIR = Path("frontend/public/case-studies")
ARTICLES_OUTPUT_DIR = OUTPUT_DIR / "articles"

def build_static_case_studies():
    """
    Parses all markdown case studies and generates static JSON files
    for the frontend to consume.
    """
    print("Starting build of case studies...")

    # Ensure output directories exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    ARTICLES_OUTPUT_DIR.mkdir(exist_ok=True)

    studies_metadata = []
    tags = {"countries": set(), "industries": set(), "pillars": set()}

    if not CASE_STUDIES_SRC_DIR.exists():
        print(f"Source directory not found: {CASE_STUDIES_SRC_DIR}")
        return

    for filename in os.listdir(CASE_STUDIES_SRC_DIR):
        if filename.endswith(".md"):
            print(f"Processing {filename}...")
            filepath = CASE_STUDIES_SRC_DIR / filename
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    content = f.read()
                    parts = content.split('---', 2)
                    if len(parts) < 3:
                        print(f"  Warning: Skipping {filename}, couldn't find YAML frontmatter.")
                        continue

                    frontmatter_str, markdown_content = parts[1], parts[2]
                    metadata = yaml.safe_load(frontmatter_str)
                    slug = metadata.get('slug', Path(filename).stem)

                    # --- Collect metadata for the index ---
                    study_tags = metadata.get('tags', {})
                    studies_metadata.append({
                        "title": metadata.get('title', 'No Title'),
                        "author": metadata.get('author', 'No Author'),
                        "date": metadata.get('date', 'No Date'),
                        "thumbnail": metadata.get('thumbnail', ''),
                        "tags": study_tags,
                        "slug": slug
                    })

                    # --- Write individual article JSON ---
                    article_data = {
                        "title": metadata.get('title', 'No Title'),
                        "author": metadata.get('author', 'No Author'),
                        "date": metadata.get('date', 'No Date'),
                        "thumbnail": metadata.get('thumbnail', ''),
                        "tags": study_tags,
                        "slug": slug,
                        "content": markdown_content.strip()
                    }
                    with open(ARTICLES_OUTPUT_DIR / f"{slug}.json", 'w', encoding='utf-8') as article_f:
                        json.dump(article_data, article_f, indent=2)

                    # --- Collect tags for filtering ---
                    for country in study_tags.get('countries', []):
                        tags["countries"].add(country)
                    for industry in study_tags.get('industries', []):
                        tags["industries"].add(industry)
                    for pillar in study_tags.get('pillars', []):
                        tags["pillars"].add(pillar)

                except Exception as e:
                    print(f"  Error processing {filename}: {e}")
    
    # --- Write the main index JSON ---
    studies_metadata.sort(key=lambda s: s['date'], reverse=True)
    available_tags = {k: sorted(list(v)) for k, v in tags.items()}
    
    index_data = {
        "studies": studies_metadata,
        "available_tags": available_tags
    }

    with open(OUTPUT_DIR / "index.json", 'w', encoding='utf-8') as index_f:
        json.dump(index_data, index_f, indent=2)

    print(f"Build complete. Wrote {len(studies_metadata)} articles.")
    print(f"Index file created at: {OUTPUT_DIR / 'index.json'}")

if __name__ == "__main__":
    build_static_case_studies()
