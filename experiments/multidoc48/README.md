# German multi-document precedence benchmark

Both fields exact: 24/48 (50.0%). Source choice: 42/48 (87.5%). Determination: 24/48 (50.0%).

See REPORT.md, PROTOCOL.md and ERRORS.md; complete native scores are in results/predictions.jsonl. Three fictional documents per case; 48 German cases across banking, insurance and finance. AI-authored and independently AI-reviewed, not human-expert validated or representative.

The new source/determination schema distinguishes unknown governing source from unknown final answer. All 48 cases and every error are retained. Frozen scientific bytes are preserved under public curation. Reproduce with scripts/reproduce.sh after preparing the exact pinned runtime in a fresh environment; weights are not distributed. Use scripts/verify_export.py to verify a finished public archive.
