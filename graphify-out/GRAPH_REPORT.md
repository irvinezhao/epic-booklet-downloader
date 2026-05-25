# Graph Report - .  (2026-05-22)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 29 nodes · 40 edges · 4 communities (3 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `211510e6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]

## God Nodes (most connected - your core abstractions)
1. `EpicClient` - 8 edges
2. `process_book()` - 7 edges
3. `main()` - 5 edges
4. `compute_reqsig()` - 4 edges
5. `EpicClientAuthTests` - 3 edges
6. `compute_pass_hash()` - 3 edges
7. `download_pages()` - 3 edges
8. `create_booklet_pdf()` - 3 edges
9. `sanitize_filename()` - 3 edges
10. `Compute the reqSig parameter for Epic API requests.          Algorithm (reverse-` - 1 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `process_book()`  [EXTRACTED]
  scripts/epic_downloader.py → scripts/epic_downloader.py  _Bridges community 1 → community 0_

## Communities (4 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.27
Nodes (6): EpicClient, main(), Make a signed GET request to the Epic API., Fetch full book metadata including page image URLs., Fetch all book IDs from a collection/favorites., Epic API client with automatic authentication and signature generation.

### Community 1 - "Community 1"
Cohesion: 0.31
Nodes (8): create_booklet_pdf(), download_pages(), process_book(), Download all page images and return paths of successfully downloaded files., Create a saddle-stitch booklet PDF from page images.          The pages are reor, Remove unsafe characters from filename., Download a single book and generate its booklet PDF., sanitize_filename()

### Community 2 - "Community 2"
Cohesion: 0.33
Nodes (5): compute_pass_hash(), compute_reqsig(), Authenticate and obtain a JWT token, unless one was provided., Compute the reqSig parameter for Epic API requests.          Algorithm (reverse-, Compute the password hash for Epic login.          Algorithm (reverse-engineered

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EpicClient` connect `Community 0` to `Community 1`, `Community 2`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Why does `process_book()` connect `Community 1` to `Community 0`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `compute_reqsig()` connect `Community 2` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **What connects `Compute the reqSig parameter for Epic API requests.          Algorithm (reverse-`, `Compute the password hash for Epic login.          Algorithm (reverse-engineered`, `Epic API client with automatic authentication and signature generation.` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._