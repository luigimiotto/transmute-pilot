import csv
from pathlib import Path
import streamlit as st

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
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;500;600;700&display=swap');
:root { --ink: #18324A; --gold: #C39A43; --paper: #FBF9F4; }
html, body, [class*="st-"] { font-family: 'Noto Serif TC', 'Noto Serif CJK TC', 'Songti TC', serif; }
[data-testid="stAppViewContainer"] { background: var(--paper); }
[data-testid="stHeader"] { background: transparent; }
.hero { text-align:center; padding: 2.4rem 0 1rem; }
.hero h1 { color: var(--ink); font-size: clamp(3.1rem, 6vw, 5rem); letter-spacing: .04em; margin: 0; }
.hero .subtitle { color: #526476; font-size: 1.22rem; margin-top: .4rem; }
.hero-rule { width: 92px; height: 3px; background: var(--gold); margin: 1.2rem auto 1.6rem; }
[data-testid="stSidebar"] { background: #F0EEE7; }
</style>
<div class="hero"><h1>TransMuTe</h1><div class="hero-rule"></div><div class="subtitle">Chinese Translation of Music Theory Terminology</div></div>
""", unsafe_allow_html=True)
st.markdown("Search historical forms, English concepts, modern Chinese equivalents, Pinyin, or passage text. Move from an individual attestation to comparison across sources.")

concept_by_id = {r["concept_id"]: r for r in concepts}
source_by_id = {r["source_id"]: r for r in sources}
witness_by_id = {r["witness_id"]: r for r in witnesses}
att_by_id = {r["attestation_id"]: r for r in attestations}
layers_by_att = {}
for x in layers: layers_by_att.setdefault(x["attestation_id"], []).append(x)
interp_by_att = {}
for x in interpretations: interp_by_att.setdefault(x["attestation_id"], []).append(x)

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

with st.sidebar:
    st.header("Narrow the corpus")
    source_options = [source_label(s["source_id"]) for s in sources if s.get("source_id")]
    selected_source_labels = st.multiselect("Source", source_options, default=source_options)
    label_to_concept = {concept_label(c): c for c in concepts if c.get("preferred_label_en")}
    selected_concept_labels = st.multiselect("Concept", list(label_to_concept))
    st.divider()
    st.caption(f"{len(attestations)} attestations · {len(concepts)} concepts")

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
        concept = concept_by_id.get(a.get("concept_id", ""), {})
        if selected_source_labels and source_label(a.get("source_id", "")) not in selected_source_labels: continue
        if selected_concept_labels and concept_label(concept) not in selected_concept_labels: continue
        # Search the normalized index, raw attestation, linked concept (including its modern Chinese label), and source metadata.
        searchable = haystack(list(ix.values()) + list(a.values()) + list(concept.values()) + list(src.values()))
        if not q or q in searchable:
            found.append((a, src, concept))
    st.subheader(f"{len(found)} matching attestations")
    if not found: st.info("No matches. Try another spelling or clear a filter.")
    for a,src,concept in found:
        title=f"{a.get('term_form_as_seen','')} · {source_label(a.get('source_id',''))} · {a.get('source_locator_verbatim','')}"
        with st.expander(title):
            c1,c2=st.columns([1,2])
            with c1:
                st.markdown(f"**Concept:** {concept_label(concept) or 'Unlinked'}")
                st.markdown(f"**Source:** {source_label(a.get('source_id',''))}")
                st.markdown(f"**Witness:** {witness_by_id.get(a.get('witness_id',''),{}).get('witness_description','')}")
                st.markdown(f"**Record ID:** `{a.get('attestation_id','')}`")
            with c2:
                st.markdown("**Source form**")
                st.write(a.get("term_form_as_seen", ""))
                st.markdown("**Context (transcribed)**")
                st.text(a.get("context_passage_verbatim", ""))
                if a.get("definition_or_explanation_verbatim"):
                    st.markdown("**Definition / explanation**")
                    st.text(a["definition_or_explanation_verbatim"])
            ls=layers_by_att.get(a.get("attestation_id",""),[])
            if ls:
                st.markdown("**Editorial layers**")
                for layer in ls: st.write(f"{layer.get('layer_type','')}: {layer.get('text_value','')} ({layer.get('source_or_editorial_status','')})")
            ins=interp_by_att.get(a.get("attestation_id",""),[])
            if ins:
                st.markdown("**Interpretation**")
                for it in ins: st.write(it.get("analysis_notes", ""))
else:
    selected = st.selectbox("Choose a concept", list(label_to_concept)) if label_to_concept else None
    if selected:
        concept = label_to_concept[selected]
        st.subheader(f"Zoom out · {selected}")
        st.write(concept.get("scope_note", ""))
        linked=[]
        for a in attestations:
            if a.get("concept_id") != concept.get("concept_id"): continue
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
                    st.markdown("**Interpretive note**"); st.write(it.get("analysis_notes", ""))

st.divider()
st.subheader("Pilot sources")
for source in sources:
    sid=source.get("source_id", "")
    with st.expander(source_label(sid)):
        st.write(source.get("bibliographic_citation", ""))
        wid=next((x for x in witnesses if x.get("source_id")==sid), None)
        if wid: st.caption("Witness: " + wid.get("witness_description", ""))

with st.expander("About the project"):
    st.markdown("""TransMuTe treats specialized terminology as historical evidence of translation and knowledge-making. Rather than presenting a continuous evolution of terms, the project compares selected transcultural moments and their distinct institutional settings. The pilot dataset is the empirical foundation for a doctoral dissertation and is designed to support both close reading of individual attestations and comparison across sources.""")
    st.markdown("**TransMuTe** is used here as a shorthand for *Transcultural Music Terminology*. The name also gestures toward the project’s interest in transformation through translation; it does not imply that meanings change in a single, linear direction.")
with st.expander("Scope and caveats"):
    st.markdown("""This pilot samples three sources: early Qing court translation, represented by 律呂纂要 (ca. 1690) and 律呂正義續編 (1713), and missionary-era translation, represented by 西國樂法啓蒙 (1872). It is a selective qualitative sample, not a comprehensive inventory or a continuous history of Chinese music terminology. Uneven source coverage is intentional at this stage. Search results identify textual matches; they do not by themselves establish conceptual equivalence. Source forms, editorial layers, and interpretations are kept distinct, and interpretive claims should be read with their evidence and confidence in view. The project begins in the late seventeenth century as a sampling decision, not as a claim that earlier transcultural musical exchange did not occur.""")
st.caption("Source wording, editorial layers, and analytical interpretations are displayed separately. This is a pilot database; verify citations and transcriptions against the cited witnesses.")
