import csv
from pathlib import Path
import unittest
from data_model import ConceptModel

BASE = Path(__file__).parent / 'data'
def read(name):
    with (BASE / (name+'.tsv')).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

class ModelTests(unittest.TestCase):
    def test_published_data_integrity(self):
        names = ['sources','witnesses','concepts','attestations','layers','interpretations','search_index']
        ids = ['source_id','witness_id','concept_id','attestation_id','layer_id','interpretation_id','search_record_id']
        tables = {n:read(n) for n in names}
        for n, key in zip(names, ids):
            self.assertEqual(len(tables[n]), len({r[key] for r in tables[n]}), n)
        parents = {r['witness_id']:r['source_id'] for r in tables['witnesses']}
        sources = {r['source_id'] for r in tables['sources']}
        att = {r['attestation_id']:r for r in tables['attestations']}
        for r in att.values():
            self.assertIn(r['source_id'], sources)
            self.assertEqual(r['source_id'], parents[r['witness_id']])
        for n in ['layers','interpretations','search_index']:
            for r in tables[n]: self.assertIn(r['attestation_id'], att)
        model = ConceptModel(tables['concepts'], tables['interpretations'])
        for r in tables['interpretations']:
            self.assertIn(r['mapping_role'], ['primary','alternative'])
            self.assertTrue(r['analysis_notes'].strip())
        self.assertEqual({r['attestation_id'] for r in tables['search_index']},set(att))
        self.assertEqual(len(tables['search_index']),len(att))
        for r in tables['search_index']:
            for key in ['source_id','witness_id']:
                self.assertEqual(r[key],att[r['attestation_id']][key])
        self.assertEqual(model.concept_ids('AT_C02_2'), {'C0002'})
        self.assertEqual(model.concept_ids('AT_C17_3'), {'C0017'})
        exact = [a for a in att if model.matches(a, {'C0001'})]
        expanded = [a for a in att if model.matches(a, model.descendants('C0001'))]
        self.assertGreater(len(expanded),len(exact))

    def test_alternative_claims_and_deduplication(self):
        # Synthetic test fixtures only; no proposed historical reading is published.
        cs=[{'concept_id':'broad'}, {'concept_id':'narrow','parent_concept_id':'broad'}]
        claims=[{'attestation_id':'test','concept_id':'broad','mapping_role':'primary'},
                {'attestation_id':'test','concept_id':'narrow','mapping_role':'alternative'}]
        m=ConceptModel(cs,claims)
        self.assertEqual(m.concept_ids('test'), {'broad','narrow'})
        self.assertTrue(m.matches('test',{'narrow'}))
        self.assertEqual([a for a in ['test'] if m.matches(a,m.descendants('broad'))],['test'])
        self.assertEqual(m.concept_ids('unlinked'),set())

    def test_invalid_hierarchies_and_links(self):
        for cs in [[{'concept_id':'a','parent_concept_id':'a'}],
                   [{'concept_id':'a','parent_concept_id':'b'},{'concept_id':'b','parent_concept_id':'a'}],
                   [{'concept_id':'a','parent_concept_id':'missing'}]]:
            with self.assertRaises(ValueError): ConceptModel(cs,[])
        with self.assertRaises(ValueError):
            ConceptModel([{'concept_id':'a'}],[{'attestation_id':'test','concept_id':'missing'}])

if __name__=='__main__': unittest.main()
