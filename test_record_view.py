import unittest
from html.parser import HTMLParser
from record_view import render_record
from test_data_model import read

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.sections=0
    def handle_data(self, data): self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag=='section': self.sections+=1

class ViewTests(unittest.TestCase):
    def test_all_records_keep_their_evidence_and_claims(self):
        cs={r['concept_id']:r for r in read('concepts')}
        for a in read('attestations'):
            layers=[r for r in read('layers') if r['attestation_id']==a['attestation_id']]
            claims=[r for r in read('interpretations') if r['attestation_id']==a['attestation_id']]
            result=render_record(a,'Source',{},layers,claims,cs,lambda c:c['preferred_label_en'])
            parser=TextParser();parser.feed(result)
            text=''.join(parser.parts)
            self.assertEqual(parser.sections,3)
            for value in [a['term_form_as_seen'],a['context_passage_verbatim'],
                          a['definition_or_explanation_verbatim']]+[r['text_value'] for r in layers]+[r['analysis_notes'] for r in claims]:
                self.assertIn(value.replace('\r\n','\n'),text)
            self.assertLess(result.index('record-level-1'),result.index('record-level-2'))
            self.assertLess(result.index('record-level-2'),result.index('record-level-3'))

    def test_text_is_escaped_and_empty_levels_are_explicit(self):
        html=render_record({'context_passage_verbatim':'<script>alert(1)</script>\n&'},'Source',{},[],[],{},lambda c:'Concept')
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('&#10;',html)
        self.assertIn('No editorial representations recorded.',html)
        self.assertIn('No interpretation recorded.',html)

if __name__=='__main__': unittest.main()
