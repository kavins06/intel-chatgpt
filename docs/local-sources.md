# Optional private source collection

All intel workflows work without a local source index. You can provide documents directly to your assistant or use its available research tools. The local utilities are an optional way to retrieve your own authorized readings with page-level provenance. They make no network calls and upload nothing.

## Index a PDF

Python 3.10+ is required for the utilities. PDF extraction uses the optional `pypdf` package:

```bash
python3 -m pip install pypdf
python3 skills/intel/scripts/import_source.py U01 \
  --pdf /absolute/path/to/your-report.pdf \
  --title "My authorized report" \
  --data-dir /absolute/path/to/private-intel-sources
```

The command copies the PDF and stores page-indexed extracted text locally. It refuses to overwrite an existing source ID. Use custom IDs such as U01 or U02. Bibliography IDs S01-S28 are reserved for exact original files; a checksum mismatch requires a new ID so old page pointers cannot silently refer to the wrong edition.

The default data directory, when none is provided, is `skills/intel/local-sources/`. It is ignored by Git and excluded from release archives. Keeping the collection outside the checkout provides an additional clear separation.

## Read or search

Pass the same data directory before the command:

```bash
python3 skills/intel/scripts/source_library.py \
  --data-dir /absolute/path/to/private-intel-sources list

python3 skills/intel/scripts/source_library.py \
  --data-dir /absolute/path/to/private-intel-sources \
  search "risk limits" --source U01 --limit 5

python3 skills/intel/scripts/source_library.py \
  --data-dir /absolute/path/to/private-intel-sources \
  read U01 --pages 1-3
```

Alternatively, set the `INTEL_SOURCE_DIR` environment variable in your own environment. The source reader and importer both honor it. If a host materializes plugins in a read-only directory, use a writable external directory.

`list` distinguishes bibliography references from locally indexed documents. `search` reports which sources were unavailable and how many it actually searched. An absent document is not a negative search result. Search matches all supplied words lexically; use synonyms when appropriate. Scores indicate retrieval relevance, not source credibility.

## Scans and existing OCR text

The PDF importer extracts existing text; it does not perform OCR. Entirely image-based PDFs fail with an explanatory message, while sparse pages are flagged for inspection. Use an authorized local OCR tool for scanned pages, then import its output under a custom source ID:

```json
[
  {"page": 1, "text": "Your first page's extracted text", "method": "local-ocr"},
  {"page": 2, "text": "Your second page's extracted text", "method": "local-ocr"}
]
```

```bash
python3 skills/intel/scripts/import_source.py U02 \
  --pages-json /absolute/path/to/pages.json \
  --title "My OCR report" \
  --data-dir /absolute/path/to/private-intel-sources
```

JSON import needs only Python's standard library. Page numbers must start at 1 and remain in original PDF order. Keep the original accessible separately, and visually check exact quotations, numbers, tables, signs, and names. The tool cannot verify that text faithfully reproduces a source.

## Keep source data private

Do not add your local source index, PDFs, or extracted text to this public repository or its release archives. The packaging allowlist includes the public bibliography only. A private local index can contain confidential or third-party copyrighted material and has its own permissions and retention requirements.

If local files are unavailable to your assistant, use ordinary attachments or accessible sources and disclose the limitation. Do not fabricate a citation to an uninspected reading.
