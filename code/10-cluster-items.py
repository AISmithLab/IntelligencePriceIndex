#!/usr/bin/env python3
"""
Cluster gigs into comparable service items (CPI "products").

1. Extract and clean service descriptions from gig titles
2. TF-IDF vectorize
3. Cluster with hierarchical/agglomerative clustering
4. Output: item assignments for each gig

Input:  data/pilot/pilot-prices.csv
Output: data/pilot/gig-items.csv        (gig -> item mapping)
        data/pilot/item-clusters.csv    (cluster summaries)
"""

import csv
import re
from pathlib import Path
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
OUTPUT_GIGS = BASE_DIR / "data" / "pilot" / "gig-items.csv"
OUTPUT_CLUSTERS = BASE_DIR / "data" / "pilot" / "item-clusters.csv"


def clean_title(title):
    """Extract service description from Fiverr title.

    Patterns:
      "Username: I will do X for $Y on fiverr.com"
      "I will do X"
      "username : I will do X for $Y on www.fiverr.com"
    """
    if not title:
        return ""

    # Remove seller prefix (various formats)
    # "Username: I will" or "username : I will"
    title = re.sub(r'^[^:]+:\s*', '', title, count=1)

    # Remove price suffix: "for $X on fiverr.com" or "for $X on www.fiverr.com"
    title = re.sub(r'\s+for\s+\$[\d,]+\s+on\s+(?:www\.)?fiverr\.com\s*$', '', title, flags=re.IGNORECASE)

    # Remove "I will " prefix
    title = re.sub(r'^I will\s+', '', title, flags=re.IGNORECASE)

    # Normalize whitespace
    title = ' '.join(title.split())

    return title.strip().lower()


def clean_slug(slug):
    """Convert slug to readable description."""
    if not slug:
        return ""
    # Remove common prefixes
    slug = re.sub(r'^i-will-', '', slug)
    # Replace hyphens with spaces
    return slug.replace('-', ' ').lower()


def get_gig_description(row):
    """Get best available description for a gig."""
    title = clean_title(row.get('title', ''))
    if title and len(title) > 10:
        return title
    slug = clean_slug(row.get('slug', ''))
    return slug


def main():
    print("Step 1: Loading and cleaning gig descriptions...")

    # Load all rows, deduplicate to one description per gig
    gig_data = {}  # (seller, slug) -> {description, titles, prices, reviews, dates}
    all_rows = []

    with open(INPUT) as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)
            key = (row['seller'], row['slug'])
            if key not in gig_data:
                gig_data[key] = {
                    'descriptions': [],
                    'prices': [],
                    'reviews': [],
                    'dates': [],
                }
            desc = get_gig_description(row)
            if desc:
                gig_data[key]['descriptions'].append(desc)
            try:
                p = float(row.get('price_basic', 0))
                if p > 0:
                    gig_data[key]['prices'].append(p)
            except (ValueError, TypeError):
                pass
            try:
                r = int(row.get('review_count', 0) or 0)
                if r > 0:
                    gig_data[key]['reviews'].append(r)
            except (ValueError, TypeError):
                pass
            gig_data[key]['dates'].append(row.get('date', ''))

    # Pick the most common (longest) description for each gig
    gig_descs = {}
    for key, data in gig_data.items():
        descs = data['descriptions']
        if descs:
            # Use the longest description (most informative)
            gig_descs[key] = max(descs, key=len)
        else:
            gig_descs[key] = clean_slug(key[1])

    print(f"  {len(gig_descs):,} unique gigs")

    # Show sample descriptions
    import random; random.seed(42)
    sample_keys = random.sample(list(gig_descs.keys()), min(10, len(gig_descs)))
    print("\n  Sample cleaned descriptions:")
    for k in sample_keys:
        print(f"    {gig_descs[k][:80]}")

    print("\nStep 2: TF-IDF vectorization...")

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    import numpy as np

    keys = list(gig_descs.keys())
    descriptions = [gig_descs[k] for k in keys]

    # TF-IDF with bigrams
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        stop_words='english',
        min_df=2,
        max_df=0.5,
    )
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    print(f"  TF-IDF matrix: {tfidf_matrix.shape}")

    # Remove zero vectors (gigs with no meaningful terms)
    import numpy as np
    norms = np.sqrt(tfidf_matrix.multiply(tfidf_matrix).sum(axis=1)).A1
    nonzero_mask = norms > 0
    zero_count = (~nonzero_mask).sum()
    if zero_count > 0:
        print(f"  Removing {zero_count} gigs with empty TF-IDF vectors")
        tfidf_matrix = tfidf_matrix[nonzero_mask]
        keys = [k for k, m in zip(keys, nonzero_mask) if m]
        descriptions = [d for d, m in zip(descriptions, nonzero_mask) if m]
        print(f"  Remaining: {len(keys)} gigs")

    print("\nStep 3: Finding optimal number of clusters...")

    # Use cosine distance via normalized vectors
    from sklearn.preprocessing import normalize
    tfidf_norm = normalize(tfidf_matrix)
    tfidf_dense = tfidf_norm.toarray()

    best_k = 50
    best_score = -1

    for k in [30, 50, 75, 100, 150]:
        clustering = AgglomerativeClustering(
            n_clusters=k,
            metric='cosine',
            linkage='average',
        )
        labels = clustering.fit_predict(tfidf_dense)
        score = silhouette_score(tfidf_dense, labels, metric='cosine', sample_size=min(2000, len(keys)))
        print(f"  k={k:>4}: silhouette={score:.3f}")
        if score > best_score:
            best_score = score
            best_k = k

    print(f"\n  Best k={best_k} (silhouette={best_score:.3f})")

    print(f"\nStep 4: Clustering with k={best_k}...")

    clustering = AgglomerativeClustering(
        n_clusters=best_k,
        metric='cosine',
        linkage='average',
    )
    labels = clustering.fit_predict(tfidf_dense)

    # Build cluster summaries
    cluster_info = defaultdict(lambda: {
        'gigs': [], 'descriptions': [], 'prices': [], 'reviews': [],
    })

    for i, key in enumerate(keys):
        cluster_id = labels[i]
        data = gig_data[key]
        cluster_info[cluster_id]['gigs'].append(key)
        cluster_info[cluster_id]['descriptions'].append(gig_descs[key])
        cluster_info[cluster_id]['prices'].extend(data['prices'])
        cluster_info[cluster_id]['reviews'].extend(data['reviews'])

    # Generate cluster labels from top TF-IDF terms
    feature_names = vectorizer.get_feature_names_out()

    cluster_labels = {}
    for cid, info in cluster_info.items():
        # Get centroid
        member_indices = [i for i, l in enumerate(labels) if l == cid]
        centroid = tfidf_matrix[member_indices].mean(axis=0).A1
        top_term_indices = centroid.argsort()[-5:][::-1]
        top_terms = [feature_names[idx] for idx in top_term_indices]
        cluster_labels[cid] = ' | '.join(top_terms)

    print(f"\n  {len(cluster_info)} clusters created")

    # Print top clusters
    print("\n  Top 20 clusters by gig count:")
    print(f"  {'ID':>4} {'Gigs':>5} {'Med$':>6} {'Label'}")
    print(f"  {'-'*4} {'-'*5} {'-'*6} {'-'*50}")

    sorted_clusters = sorted(cluster_info.items(), key=lambda x: -len(x[1]['gigs']))
    for cid, info in sorted_clusters[:20]:
        n_gigs = len(info['gigs'])
        med_price = sorted(info['prices'])[len(info['prices'])//2] if info['prices'] else 0
        print(f"  {cid:>4} {n_gigs:>5} ${med_price:>5.0f} {cluster_labels[cid][:50]}")

    # Step 5: Write outputs
    print("\nStep 5: Writing outputs...")

    # Gig -> item mapping
    gig_to_cluster = {keys[i]: labels[i] for i in range(len(keys))}

    with open(OUTPUT_GIGS, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['seller', 'slug', 'item_id', 'item_label', 'description'])
        for key in sorted(keys):
            cid = gig_to_cluster[key]
            writer.writerow([
                key[0], key[1], cid,
                cluster_labels[cid],
                gig_descs[key],
            ])

    # Cluster summaries
    with open(OUTPUT_CLUSTERS, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'item_id', 'label', 'n_gigs', 'n_sellers',
            'median_price', 'mean_price',
            'median_reviews', 'sample_descriptions',
        ])
        for cid in sorted(cluster_info.keys()):
            info = cluster_info[cid]
            sellers = set(k[0] for k in info['gigs'])
            med_price = sorted(info['prices'])[len(info['prices'])//2] if info['prices'] else 0
            mean_price = sum(info['prices']) / len(info['prices']) if info['prices'] else 0
            med_reviews = sorted(info['reviews'])[len(info['reviews'])//2] if info['reviews'] else 0
            # Sample 3 descriptions
            sample = info['descriptions'][:3]
            writer.writerow([
                cid, cluster_labels[cid], len(info['gigs']), len(sellers),
                f'{med_price:.2f}', f'{mean_price:.2f}',
                med_reviews,
                ' ||| '.join(sample),
            ])

    print(f"\n  Gig mapping: {OUTPUT_GIGS}")
    print(f"  Cluster summaries: {OUTPUT_CLUSTERS}")

    # Final stats
    print(f"\n{'='*60}")
    print("ITEM CLUSTERING SUMMARY")
    print(f"{'='*60}")
    print(f"  Total gigs:        {len(keys):,}")
    print(f"  Service items:     {len(cluster_info)}")
    print(f"  Avg gigs/item:     {len(keys)/len(cluster_info):.1f}")
    sizes = [len(info['gigs']) for info in cluster_info.values()]
    print(f"  Largest cluster:   {max(sizes)} gigs")
    print(f"  Smallest cluster:  {min(sizes)} gigs")
    print(f"  Singleton items:   {sum(1 for s in sizes if s == 1)}")


if __name__ == "__main__":
    main()
