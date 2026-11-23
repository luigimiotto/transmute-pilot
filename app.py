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
st.title("TransMuTe")
st.caption("Pilot database · Sino-European music-theory terminology")
st.markdown("Search historical forms, English concepts, Pinyin, or passage text. Open a result to move from the attestation to its comparative concept context.")

concept_by_id = {r["concept_id"]: r for r in concepts}
source_by_id = {r["source_id"]: r for r in sources}
witness_by_id = {r["witness_id"]: r for r in witnesses}
att_by_id = {r["attestation_id"]: r for r in attestations}
layers_by_att = {}
for x in layers: layers_by_att.setdefault(x["attestation_id"], []).append(x)
interp_by_att = {}
for x in interpretations: interp_by_att.setdefault(x["attestation_id"], []).append(x)

with st.sidebar:
    st.header("Narrow the corpus")
    source_options = sorted({r["short_title"] for r in sources if r.get("source_short_title")})
    chosen_sources = st.multiselect("Source", source_options, default=source_options)
    concept_options = sorted({r["preferred_label_en"] for r in concepts if r.get("preferred_label_en")})
    chosen_concepts = st.multiselect("Concept", concept_options)
    st.divider()
    st.caption(f"{len(attestations)} attestations · {len(concepts)} concepts")

query = st.text_input("Search the corpus", placeholder="Try 品, 啟發, pǐn, clef, soprano…")
mode = st.radio("View", ["Search attestations", "Compare a concept"], horizontal=True)

def matches(row, q):
    if not q:
        return True
    qf=q.casefold()
    return qf in " ".join(str(v or "") for v in row.values()).casefold()

if mode == "Search attestations":
    found=[]
    for ix in search_index:
        aid=ix.get("attestation_id", "")
        a=att_by_id.get(aid)
        if not a: continue
        src=source_by_id.get(a.get("source_id", ""), {})
        concept=concept_by_id.get(a.get("concept_id", ""), {})
        if chosen_sources and src.get("short_title") not in chosen_sources: continue
        if chosen_concepts and concept.get("preferred_label_en") not in chosen_concepts: continue
        if matches(ix, query) or (query and query.casefold() in " ".join(a.values()).casefold()): found.append((a,src,concept))
    st.subheader(f"{len(found)} matching attestations")
    if not found: st.info("No matches. Try a shorter form, another spelling, or clear a filter.")
    for a,src,concept in found:
        title=f"{a.get('term_form_as_seen','')} · {src.get('short_title','source')} · {a.get('source_locator_verbatim','')}"
        with st.expander(title):
            c1,c2=st.columns([1,2])
            with c1:
                st.markdown(f"**Concept:** {concept.get('preferred_label_en','Unlinked')}")
                st.markdown(f"**Source:** {src.get('title_as_published',src.get('short_title',''))} ({src.get('date','')})")
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
                for layer in ls:
                    st.write(f"{layer.get('layer_type','')}: {layer.get('text_value','')} ({layer.get('source_or_editorial_status','')})")
            ins=interp_by_att.get(a.get("attestation_id",""),[])
            if ins:
                st.markdown("**Interpretation**")
                for it in ins: st.write(it.get("analysis_notes", ""))

else:
    label_to_concept={r.get("preferred_label_en", ""):r for r in concepts}
    selected=st.selectbox("Choose a concept", list(label_to_concept)) if label_to_concept else None
    if selected:
        concept=label_to_concept[selected]
        st.subheader(f"Zoom out · {selected}")
        st.write(concept.get("scope_note", ""))
        linked=[]
        for a in attestations:
            if a.get("concept_id") != concept.get("concept_id"): continue
            src=source_by_id.get(a.get("source_id", ""), {})
            if chosen_sources and src.get("short_title") not in chosen_sources: continue
            linked.append((a,src))
        st.caption(f"{len(linked)} linked attestations across the selected witnesses")
        for a,src in linked:
            with st.expander(f"{a.get('term_form_as_seen','')} · {src.get('short_title','')} · {a.get('source_locator_verbatim','')}"):
                st.markdown("**Source context**")
                st.text(a.get("context_passage_verbatim", ""))
                st.markdown("**Definition / explanation**")
                st.text(a.get("definition_or_explanation_verbatim", ""))
                for layer in layers_by_att.get(a.get("attestation_id",""),[]):
                    st.write(f"{layer.get('layer_type','')}: {layer.get('text_value','')}")
                for it in interp_by_att.get(a.get("attestation_id",""),[]):
                    st.markdown("**Interpretive note**")
                    st.write(it.get("analysis_notes", ""))

st.divider()
st.caption("Source wording, editorial layers, and analytical interpretations are displayed separately. This is a pilot dataset; verify citations and transcriptions against the cited witnesses.")

