# Workshop schema revision — 26 November 2026

This working revision develops the v0.1.0-pilot framework. It does not change the files already deposited as that version on Zenodo. Cite a new deposit/version for this revised schema when one is released.

## Concept assignments are interpretive claims

`interpretations.tsv` now has `concept_id` and `mapping_role` (`primary` or `alternative`). Each existing assignment has been moved from its attestation into its existing interpretation, retaining the original analysis, references, provisional status, and blank confidence. No competing historical reading has been invented. Additional, separately identified interpretations may propose other concepts for the same attestation and must supply their supporting argument and references.

`attestations.tsv` and `search_index.tsv` retain a deprecated primary-concept cache in `concept_id` for compatibility with older application processes during deployment. The revised app ignores these cache fields and obtains authoritative concept assignments through interpretation records. Regenerate the cache from primary interpretations when mappings change; it does not describe all possible readings. Non-rejected concept-bearing interpretations participate in comparison, including provisional and alternative readings; their role and status are displayed. An occurrence appears once per comparison even if multiple readings match. Interpretations without a concept may still hold general analytical notes.

## Broader and narrower categories

`concepts.tsv` now has an optional `parent_concept_id`. Treble, alto, and bass clef link to clef. Soprano, alto, tenor, and bass link to the existing voice-type category. These are editorial navigation relationships between comparative categories, not claims that historical authors used this taxonomy. No other hierarchy has been inferred.

This is a single-parent hierarchy: one category can have zero or one broader category, and a broader category can have many narrower categories. Multiple parents would require a separate relations table. Cycles and missing parents are rejected by the model. The comparison view defaults to exact-category matches and offers an explicit “Include narrower categories” checkbox; selecting it includes all descendants. Search filters remain exact-category filters, while text search includes the labels of all linked concepts.

## Identifier repairs

Duplicate layer IDs were disambiguated by appending their linked attestation IDs: `LYG_C01_1` on `AT_C01_1_2` became `LYG_C01_1__AT_C01_1_2`; `LYG_C02_3` on `AT_C02_3_2` became `LYG_C02_3__AT_C02_3_2`. Source transcriptions, layer text, passages, locators, and analysis notes were preserved.

## Validation

Run `python -m unittest test_data_model.py`. Checks cover identifiers, parent references, source/witness consistency, index coverage, hierarchy cycles, descendant expansion, alternative assignments using synthetic test fixtures, and deduplication. The seven TSV tables remain; the hierarchy is a self-relation on concepts. Occurrences and concepts now form a many-to-many relationship through interpretation records.
