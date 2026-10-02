# Pre-inference visual audit

Result: PASS. All 50 planned images and all 120 primary gold fields were visually reviewed without accessing model predictions. No gold or image/label checksum mismatch was found.

Thirty chart images were inspected in five readable contact sheets. Twenty invoices were inspected individually at readable original resolution; four had already been inspected as diagnostics and were verified to be identical final copies by source ID and checksum. The observations, source IDs, expected labels and checks are recorded in `pre_inference_audit.json`.

## Fixes identified and verified before freeze

1. The horizontal sign-coded chart at chart-012/source test137 contains only positive values. Its category description now refers to a single series and a positive/negative legend, rather than requiring both positive and negative data.
2. The three pie-plus-bar examples have a vertically stacked column. The German category description now says “gestapelte Säule”; the English description also explicitly says vertical column.

Both fixes are present in German and English requests, without changing image selection or gold IDs.

## Source limitations retained

- Pie chart-016, chart-017 and chart-018 have clipped legend text. Every entry's swatch and row remains visible, so the requested count is unambiguous; exact transcription would not be suitable.
- Invoice-004, invoice-006, invoice-012 and invoice-013 show line-item VAT percentages despite an explicit §19 no-VAT notice. The question correctly prioritizes the explicit notice. The evaluation measures visible-document recognition, not legal validity.
- Review was at readable source resolution. Model-processor downscaling may reduce readability and is part of the stated runtime condition.
- Synthetic titles and axis/category semantics can be inconsistent. The chart questions measure visual structure and legend counts, not substantive financial truth.

No source record or gold needed replacement. Cases and requests may now be frozen for inference.
