"""Escaped HTML for the three scholarly layers of an occurrence."""
from html import escape

def esc(value):
    return escape(str(value or '').replace('\r\n', '\n')).replace('\n', '&#10;')

def field(label, value):
    return f'<div class="record-field"><strong>{esc(label)}</strong><div>{esc(value)}</div></div>'

def section(level, title, subtitle, content):
    return (f'<section class="record-level record-level-{level}" aria-label="{level}. {esc(title)}">'
            f'<h4>{level}. {esc(title)}</h4><p class="record-level-description">{esc(subtitle)}</p>'
            f'{content}</section>')

def render_record(attestation, source, witness, layers, claims, concepts, concept_label):
    evidence = field('Source', source)
    evidence += field('Consulted witness', witness.get('witness_description', ''))
    evidence += field('Location', attestation.get('source_locator_verbatim', ''))
    evidence += field('Record ID', attestation.get('attestation_id', ''))
    evidence += field('Source form', attestation.get('term_form_as_seen', ''))
    evidence += field('Context (transcribed)', attestation.get('context_passage_verbatim', ''))
    if attestation.get('definition_or_explanation_verbatim'):
        evidence += field('Definition / explanation in the source', attestation['definition_or_explanation_verbatim'])

    editorial = ''
    names = {'romanization':'Romanization', 'working_gloss':'Working English gloss'}
    for layer in layers:
        editorial += field(names.get(layer.get('layer_type'), layer.get('layer_type', 'Editorial representation')),
                           layer.get('text_value', ''))
        detail = ' · '.join(x for x in [layer.get('scheme_or_language', ''),
                                       layer.get('source_or_editorial_status', '')] if x)
        if detail: editorial += f'<p class="record-note">{esc(detail)}</p>'
    if not layers: editorial = '<p>No editorial representations recorded.</p>'

    interpretation = ''
    for claim in claims:
        cid = claim.get('concept_id', '')
        label = concept_label(concepts[cid]) if cid else 'Analytical note'
        interpretation += f'<article class="record-claim"><h5>{esc(label)}</h5>'
        interpretation += field('Reading / status', ' · '.join(x for x in [claim.get('mapping_role', ''),
                                                                          claim.get('epistemic_status', '')] if x) or 'Not stated')
        interpretation += f'<div class="record-analysis">{esc(claim.get("analysis_notes", ""))}</div>'
        refs = claim.get('source_notes', '')
        if refs and not refs.startswith('[YOU FILL'):
            interpretation += field('Evidence / references', refs)
        if claim.get('confidence'): interpretation += field('Confidence', claim['confidence'])
        interpretation += '</article>'
    if not claims: interpretation = '<p>No interpretation recorded.</p>'
    return ('<div class="record-layers">' +
            section(1, 'Source evidence and provenance', 'Transcribed wording and the consulted witness', evidence) +
            section(2, 'Editorial representations', 'Reading aids added by the researcher', editorial) +
            section(3, 'Interpretation and comparison', 'Proposed readings, supporting notes, and status', interpretation) +
            '</div>')
