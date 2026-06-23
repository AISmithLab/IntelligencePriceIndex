from pathlib import Path
import csv

BASE = Path("data/cdx-index/raw-2025")
OUT = Path("data/cdx-index/gig-index.tsv")

def parse_line(line):
    parts = line.strip().split()
    if len(parts) < 3:
        return None

    urlkey = parts[0]
    timestamp = parts[1]
    original = parts[2]

    if "fiverr.com" not in original:
        return None

    try:
        path = original.split("fiverr.com/")[1].split("?")[0]
    except:
        return None

    parts = path.strip("/").split("/")
    if len(parts) < 2:
        return None

    seller = parts[0]
    slug = parts[1]

    # filter junk/system paths
    if seller in ["C$", "404", "search"]:
        return None

    return seller, slug, timestamp, original


def main():
    seen = set()
    rows = []

    for file in BASE.glob("*.tsv"):
        with open(file, "r", errors="ignore") as f:
            for line in f:
                r = parse_line(line)
                if not r:
                    continue

                seller, slug, ts, url = r
                key = (seller, slug, ts)

                if key in seen:
                    continue

                seen.add(key)
                rows.append((seller, slug, ts, url))

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUT, "w") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["seller", "slug", "timestamp", "url"])
        w.writerows(rows)

    print("DONE:", len(rows))


if __name__ == "__main__":
    main()
