# TransMuTe

**Chinese Translation of Music Theory Terminology**

TransMuTe is a pilot digital humanities project exploring how European music-theory concepts were rendered and reframed in Chinese texts. It treats historical terminology as evidence of translation and knowledge-making, while keeping source wording, editorial readings, and scholarly interpretations distinct.

## About this pilot

This pilot samples selected passages from three works:

- *Lülü zuanyao* 律呂纂要 (ca. 1690)
- *Lülü zhengyi xubian* 律呂正義續編 (1713)
- *Xiguo yuefa qimeng* 西國樂法啓蒙 (1872)

The sample is selective and qualitative. It is not a comprehensive inventory or a continuous history of Chinese music terminology. Its starting date reflects the sources selected for this pilot, not a claim that earlier musical exchanges did not occur.

Search results identify textual matches; they do not by themselves establish that a historical Chinese term is conceptually equivalent to a modern English label. Interpretations are analytical proposals and should be read alongside their source evidence and stated uncertainty.

## Explore the database

Use **Zoom in** to search for historical Chinese forms, English concepts, modern Chinese labels, pinyin, or passage text. Each result represents an attestation in a particular source witness and location.

Use **Zoom out** to compare attestations grouped under a concept across the selected sources. The same Chinese form may occur in different conceptual contexts; the records preserve those occurrences separately.

The interface presents source forms and passages alongside editorial layers such as romanization or working glosses and separate analytical interpretations. Page images are not embedded in this pilot.

## Data and structure

The tabular data are in the `data/` directory as UTF-8 tab-separated files:

- `concepts.tsv` — English concepts and modern Chinese search labels.
- `sources.tsv` — bibliographic records for the works.
- `witnesses.tsv` — consulted editions or copies of those works.
- `attestations.tsv` — individual term occurrences, with location and textual context.
- `layers.tsv` — editorial forms linked to attestations, such as romanization and glosses.
- `interpretations.tsv` — analytical claims linked to attestations.
- `search_index.tsv` — searchable forms and text mapped back to attestations.

An attestation is the central evidence record. Each attestation links to a source and witness. Interpretations link occurrences to one or more proposed concepts, with a primary or alternative role and an epistemic status. Concepts can link to one broader category through parent_concept_id. One attestation can have multiple editorial layers and multiple interpretations. Search-index records point back to attestations so that a user can find the same record by different forms.

The website is a read-only interface to these tables. The TSV files are available in this repository for inspection. Identifiers connect related rows across files; do not treat rows with the same Chinese form as duplicates.

## Sources and citation

Full bibliographic information and witness notes are recorded in `data/sources.tsv` and `data/witnesses.tsv`. Cite the historical work and the specific edition or witness used, together with the printed locator recorded for the attestation. Please verify quotations and locators against the cited witness before reuse.

## Project and feedback

TransMuTe is a work in progress and the empirical engine of a doctoral dissertation. Feedback on the sampling, terminology, data structure, search experience, and interpretation is welcome. Interpretive notes are provisional where marked as such and may change as the project develops.

## License and reuse

The application code in this repository is licensed under the MIT License; see [LICENSE](LICENSE). You may fork, modify, and redistribute the software, including commercially, provided you retain the copyright and license notices.

The project dataset deposited on Zenodo is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). The same license applies to the corresponding creator-owned dataset files in this repository. Reusers must credit the creator, link to the license, and indicate changes. This license does not cover third-party historical source texts, scans, or library materials unless explicitly stated.

**Suggested project citation:** Miotto, Luigi. *TransMuTe: Chinese Translation of Music Theory Terminology* [dataset and software]. Zenodo. [https://doi.org/10.5281/zenodo.24508796](https://doi.org/10.5281/zenodo.24508796). Cite the specific version used. For historical evidence, also cite the primary work, consulted witness, and printed locator recorded in the relevant attestation.


## Workshop schema revision

See [SCHEMA_CHANGELOG.md](SCHEMA_CHANGELOG.md) for the migration from the deposited v0.1.0-pilot schema. The live working app supports alternative conceptual readings and optional inclusion of narrower categories. The Zenodo v0.1.0 files remain the historical release; the workshop revision has not replaced that deposit.
