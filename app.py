import csv
from pathlib import Path
import streamlit as st
from data_model import ConceptModel

BASE = Path(__file__).parent / "data"

def read_table(name):
    path = BASE / f"{name}.tsv"
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

concepts = read_table("concepts")
sources = read_table("sources")
witnesses = read_table("witnesses")
attestations = read_table("attestations")
layers = read_table("layers")
interpretations = read_table("interpretations")
search_index = read_table("search_index")

st.set_page_config(page_title="TransMuTe | Pilot Database", page_icon="🎼", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Serif+TC:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');
:root { --ink: #18324A; --gold: #C39A43; --electric: #3478C8; --paper: #F4F8FD; }
html, body, [class*="st-"] { font-family: 'Noto Serif TC', 'Noto Serif CJK TC', 'Source Serif 4', 'Songti TC', serif; }
[data-testid="stText"], [data-testid="stCode"], pre, code { font-family: 'Noto Serif TC', 'Noto Serif CJK TC', 'Songti TC', serif !important; }
.source-cjk { font-family: 'Noto Serif TC', 'Noto Serif CJK TC', 'Songti TC', serif; white-space: pre-wrap; overflow-wrap: anywhere; }
[data-testid="stAppViewContainer"] { background: var(--paper); }
[data-testid="stHeader"] { background: transparent; }
.hero { text-align:center; padding: 2.4rem 0 1rem; }
.hero-mark { color: #343A40; font-family: 'Ma Shan Zheng', 'Noto Serif TC', serif; font-size: 3.35rem; letter-spacing: .12em; line-height: 1; margin-bottom: .55rem; }
.hero h1 { color: #343A40; font-size: clamp(3.1rem, 6vw, 5rem); letter-spacing: .04em; margin: 0; }
.hero .brand-translation { color: #355C9A; }
.hero .brand-music { color: #39756F; }
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3, [data-testid="stHeading"] h4 { color: #343A40; }
.hero .subtitle { color: #526476; font-size: 1.22rem; margin-top: .4rem; }
.hero-rule { width: 92px; height: 3px; background: var(--electric); margin: 1.2rem auto 1.6rem; }
.source-jump { text-align: center; margin: 0 0 1rem; }
.source-jump a { color: var(--ink); text-decoration-color: var(--gold); text-underline-offset: 4px; font-weight: 600; }
[data-testid="stExpander"] summary svg { display: none !important; }
[data-testid="stExpander"] summary span[data-testid="stIconMaterial"] { display: none !important; }
[data-testid="stExpander"] summary::before { content: '›'; color: var(--electric); font: 1.55rem/1 'Source Sans 3', sans-serif; margin-right: .55rem; }
[data-testid="stExpander"] details[open] summary::before { content: '⌄'; }
[data-testid="stExpander"] { border-color: #B8CCEB; }
[data-testid="collapsedControl"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stSidebar"] { background: #F0EEE7; }
</style>
<div class="hero"><div class="hero-mark"><span class="brand-translation">譯</span>變</div><h1><span class="brand-translation">Trans</span><span class="brand-music">Mu</span>Te</h1><div class="hero-rule"></div><div class="subtitle">Chinese Translation of Music Theory Terminology</div></div>
""", unsafe_allow_html=True)
st.markdown('<p class="source-jump"><a href="#pilot-sources">Explore the pilot sources ↓</a></p>', unsafe_allow_html=True)
st.markdown("Search historical forms or concepts in English, Chinese, Pinyin, or passage text. Move from an individual attestation to comparison across sources.")

concept_by_id = {r["concept_id"]: r for r in concepts}
source_by_id = {r["source_id"]: r for r in sources}
witness_by_id = {r["witness_id"]: r for r in witnesses}
att_by_id = {r["attestation_id"]: r for r in attestations}
layers_by_att = {}
for x in layers: layers_by_att.setdefault(x["attestation_id"], []).append(x)
interp_by_att = {}
for x in interpretations: interp_by_att.setdefault(x["attestation_id"], []).append(x)
model = ConceptModel(concepts, interpretations)

# Display source labels consistently by Chinese title and original publication date.
source_display = {
    "SO001": "律呂纂要 (ca. 1690)",
    "SO002": "律呂正義續編 (1713)",
    "SO003": "西國樂法啓蒙 (1872)",
}
def source_label(source_id):
    return source_display.get(source_id, source_by_id.get(source_id, {}).get("title_as_published", source_id))

def concept_label(concept):
    en = concept.get("preferred_label_en", "")
    zh = concept.get("modern_zh_label", "")
    return f"{en} · {zh}" if zh else en

def assigned_labels(attestation):
    return [concept_label(concept_by_id[cid])
            for cid in sorted(model.concept_ids(attestation['attestation_id']))]

def show_interpretation(claim):
    cid = claim.get('concept_id', '')
    if cid:
        st.markdown('**Proposed concept:** ' + concept_label(concept_by_id[cid]))
        st.caption('Reading: ' + claim.get('mapping_role', 'unspecified') +
                   ' · Status: ' + (claim.get('epistemic_status') or 'not stated'))
    st.write(claim.get('analysis_notes', ''))
    if claim.get('source_notes') and not claim['source_notes'].startswith('[YOU FILL'):
        st.caption('Evidence / references: ' + claim['source_notes'])
    if claim.get('confidence'):
        st.caption('Confidence: ' + claim['confidence'])

with st.expander("Filter the corpus", expanded=False):
    source_options = [source_label(s["source_id"]) for s in sources if s.get("source_id")]
    selected_source_labels = st.multiselect("Source", source_options, default=source_options)
    label_to_concept = {concept_label(c): c for c in concepts if c.get("preferred_label_en")}
    selected_concept_labels = st.multiselect("Concept", list(label_to_concept))
    st.divider()

query = st.text_input("Search the corpus", placeholder="Try 品, 啟發, 譜號, pǐn, clef, soprano…")
mode = st.radio("Explore", ["Zoom in · Search attestations", "Zoom out · Compare a concept"], horizontal=True)

def haystack(values):
    return " ".join(str(v or "") for v in values).casefold()

if mode.startswith("Zoom in"):
    found=[]
    q = query.strip().casefold()
    for ix in search_index:
        aid = ix.get("attestation_id", "")
        a = att_by_id.get(aid)
        if not a: continue
        src = source_by_id.get(a.get("source_id", ""), {})
        linked_concepts = [concept_by_id[cid] for cid in model.concept_ids(aid)]
        if selected_source_labels and source_label(a.get("source_id", "")) not in selected_source_labels: continue
        if selected_concept_labels and not set(assigned_labels(a)) & set(selected_concept_labels): continue
        # Search the normalized index, raw attestation, linked concept (including its modern Chinese label), and source metadata.
        searchable = haystack(list(ix.values()) + list(a.values()) +
                             [v for c in linked_concepts for v in c.values()] + list(src.values()))
        if not q or q in searchable:
            found.append((a, src, linked_concepts))
    if q:
        st.subheader(f"{len(found)} matching attestations")
    else:
        st.subheader("Browse the pilot corpus")
    if not found: st.info("No matches. Try another spelling or clear a filter.")
    for a,src,concept in found:
        with st.expander(f"{a.get('term_form_as_seen','')} · {source_label(a.get('source_id',''))} · {a.get('source_locator_verbatim','')}"):
            c1,c2=st.columns([1,2])
            with c1:
                st.markdown("**Proposed concepts:** " + ('; '.join(assigned_labels(a)) or 'Unlinked'))
                st.markdown(f"**Source:** {source_label(a.get('source_id',''))}")
                st.markdown(f"**Witness:** {witness_by_id.get(a.get('witness_id',''),{}).get('witness_description','')}")
                st.markdown(f"**Record ID:** `{a.get('attestation_id','')}`")
            with c2:
                st.markdown("**Source form**")
                st.write(a.get("term_form_as_seen", ""))
                st.markdown("**Context (transcribed)**")
                st.markdown(f"<div class='source-cjk'>{a.get('context_passage_verbatim', '')}</div>", unsafe_allow_html=True)
                if a.get("definition_or_explanation_verbatim"):
                    st.markdown("**Definition / explanation**")
                    st.markdown(f"<div class='source-cjk'>{a['definition_or_explanation_verbatim']}</div>", unsafe_allow_html=True)
            ls=layers_by_att.get(a.get("attestation_id",""),[])
            if ls:
                st.markdown("**Editorial layers**")
                for layer in ls: st.write(f"{layer.get('layer_type','')}: {layer.get('text_value','')} ({layer.get('source_or_editorial_status','')})")
            ins=interp_by_att.get(a.get("attestation_id",""),[])
            if ins:
                st.markdown("**Interpretation**")
                for it in ins: show_interpretation(it)
else:
    selected = st.selectbox("Choose a concept", list(label_to_concept)) if label_to_concept else None
    if selected:
        concept = label_to_concept[selected]
        st.subheader(f"Zoom out · {selected}")
        st.write(concept.get("scope_note", ""))
        parent_id = concept.get('parent_concept_id', '')
        if parent_id:
            st.caption('Broader category: ' + concept_label(concept_by_id[parent_id]))
        include_narrower = st.checkbox('Include narrower categories', value=False)
        selected_ids = model.descendants(concept['concept_id']) if include_narrower else {concept['concept_id']}
        st.caption('Categories are editorial tools for comparison, not a historical taxonomy. '
                   'Provisional and alternative readings may bring an occurrence into more than one category.')
        if include_narrower:
            st.caption('Included categories: ' + '; '.join(concept_label(concept_by_id[c]) for c in sorted(selected_ids)))
        linked=[]
        for a in attestations:
            if not model.matches(a['attestation_id'], selected_ids): continue
            src=source_by_id.get(a.get("source_id", ""), {})
            if selected_source_labels and source_label(a.get("source_id","")) not in selected_source_labels: continue
            linked.append((a,src))
        st.caption(f"{len(linked)} linked attestations across the selected witnesses")
        for a,src in linked:
            with st.expander(f"{a.get('term_form_as_seen','')} · {source_label(a.get('source_id',''))} · {a.get('source_locator_verbatim','')}"):
                st.markdown("**Source context**")
                st.text(a.get("context_passage_verbatim", ""))
                if a.get("definition_or_explanation_verbatim"):
                    st.markdown("**Definition / explanation**")
                    st.text(a["definition_or_explanation_verbatim"])
                for layer in layers_by_att.get(a.get("attestation_id",""),[]): st.write(f"{layer.get('layer_type','')}: {layer.get('text_value','')}")
                for it in interp_by_att.get(a.get("attestation_id",""),[]):
                    st.markdown("**Interpretive note**"); show_interpretation(it)

st.divider()
st.markdown('<div id="pilot-sources"></div>', unsafe_allow_html=True)
st.subheader("Pilot sources")
source_columns = st.columns(3)
for index, source in enumerate(sources):
    sid = source.get("source_id", "")
    with source_columns[index % len(source_columns)]:
        with st.expander(source_label(sid)):
            st.write(source.get("bibliographic_citation", ""))
            witness = next((x for x in witnesses if x.get("source_id") == sid), None)
            if witness:
                st.caption("Witness: " + witness.get("witness_description", ""))

about_col, scope_col = st.columns(2)
with about_col:
    with st.expander("About the project"):
        st.markdown("""Terminology is often (mis)understood merely as the “study of vocabulary in specialized fields” (Alleton 2001, 15). Examined through the lens of translation history, however, terms are not static containers or transfer-oriented vessels. Taking music theory as an example, this project approaches them as dynamic interfaces: historical vestiges that encapsulate specific concepts while revealing broader processes of transculturation.""")
        st.markdown("""**TransMuTe**, like the verb *to transmute*, evokes the “translingual practice” (Liu 1995) through which musical terms are reshaped in new linguistic and cultural environments. Its capitalized letters point to the **Trans**lation of **Mu**sic **Te**rminology and to its **Trans**culturation process. The name also suggests going *trans-*—beyond the silent archival pages (*MuTe*)—and unmuting the transcultural resonances of translation.""")
with scope_col:
    with st.expander("Scope and caveats"):
        st.markdown("""This pilot samples three sources: the early Qing 律呂纂要 (ca. 1690), 律呂正義續編 (1713), and the later Qing 西國樂法啓蒙 (1872). It is a selective qualitative sample, not a comprehensive inventory or an evolutionary line of Chinese music terminology. Uneven source coverage is intentional at this stage. Search results identify textual matches; they do not by themselves establish conceptual equivalence. Source forms, editorial layers, and interpretations are kept distinct, and interpretive claims should be read with their evidence and confidence in view. The project begins in the late seventeenth century as a sampling decision, not as a claim that earlier musical exchanges did not occur.""")
st.caption("Source wording, editorial layers, and analytical interpretations are displayed separately. This is a pilot database; verify citations and transcriptions against the cited witnesses.")
st.markdown("<footer class='site-footer'>Live workshop revision · <a href='https://github.com/luigimiotto/transmute-pilot/blob/main/SCHEMA_CHANGELOG.md'>Schema changes since the archived v0.1.0-pilot</a><br>TransMuTe · Created by Luigi Miotto · Please cite the project when reusing its code or data.<br><a href='https://doi.org/10.5281/zenodo.24508796' target='_blank' rel='noopener noreferrer'>Cite this project · DOI: 10.5281/zenodo.24508796</a><br>App code: MIT License · Dataset: CC BY 4.0</footer>", unsafe_allow_html=True)
