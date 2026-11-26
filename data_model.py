"""Concept links are claims; the hierarchy is editorial navigation."""

class ConceptModel:
    def __init__(self, concepts, interpretations):
        self.concepts = {c['concept_id']: c for c in concepts}
        self.claims = {}
        for claim in interpretations:
            self.claims.setdefault(claim['attestation_id'], []).append(claim)
            cid = claim.get('concept_id', '')
            if cid and cid not in self.concepts:
                raise ValueError(f"Unknown concept: {cid}")
        for cid in self.concepts:
            visited = set()
            current = cid
            while current:
                if current in visited:
                    raise ValueError(f"Concept hierarchy cycle at {current}")
                if current not in self.concepts:
                    raise ValueError(f"Unknown parent concept: {current}")
                visited.add(current)
                current = self.concepts[current].get('parent_concept_id', '')

    def concept_ids(self, attestation_id):
        return {r['concept_id'] for r in self.claims.get(attestation_id, [])
                if r.get('concept_id') and r.get('epistemic_status') != 'rejected'}

    def descendants(self, concept_id):
        result = {concept_id}
        while True:
            children = {cid for cid, c in self.concepts.items()
                        if c.get('parent_concept_id') in result}
            if children <= result:
                return result
            result |= children

    def matches(self, attestation_id, concept_ids):
        return bool(self.concept_ids(attestation_id) & set(concept_ids))
