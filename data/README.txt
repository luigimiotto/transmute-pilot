TransMuTe pilot database-ready export
Tables: concepts, sources, witnesses, attestations, layers, interpretations, search_index.
Join keys: attestations.concept_id -> concepts; source_id -> sources; witness_id -> witnesses; layers/interpretations/search_index.attestation_id -> attestations.
Chinese search: substring or full-text search over search_index.term_form, searchable_context, searchable_definition, and search_text. Do not deduplicate same forms: 品 returns all matching source attestations, retaining concept/source/context.
image_reference omitted; bracketed no-attestation forms omitted; repeated context/definition retained.
Exported 23 attestations; 46 layers; 23 interpretations; 23 search records.
