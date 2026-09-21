# Annotation guide

## Unit of annotation

Annotate one atomic claim against one identified evidence passage. Do not use outside
knowledge. If the passage is only an abstract, judge the abstract and mark its access tier;
do not infer what the unseen full text says.

## Primary relation label

- `supports`: all material parts are stated or directly implied.
- `partially_supports`: a material part is supported, while another part is missing, narrower, or
  qualified differently.
- `contradicts`: the opposite is stated or implied, including direction reversal, a null
  result versus an asserted effect, or incompatible study design/population.
- `not_addressed`: the available source evidence does not address the claim either way.
- `insufficient_context`: the excerpt is too truncated or ambiguous to apply another label.
- `source_unavailable`: the identified source could not be obtained, parsed, or supplied
  for a valid comparison.

Use `partially_supports` only when some material content is positively supported. Use
`insufficient_context` for an evidence defect, not reviewer uncertainty about a readable
study result. Use `source_unavailable` only when there is no usable source content; it is
not a semantic judgment about an available passage.

## Required secondary notes

Annotators flag every applicable mismatch:

- population or studied entity;
- endpoint or outcome;
- direction of effect;
- duration or date;
- causal strength;
- number, unit, denominator, or uncertainty interval;
- source completeness;
- study design;
- universal or absolute language;
- source identity.

## Procedure

1. Confirm DOI/title identity.
2. Read the complete supplied passage plus surrounding context.
3. Restate the claim as independently meaningful atomic components.
4. Assign the primary label.
5. Record secondary mismatch flags and a concise rationale.
6. Record whether more source context could change the label.

Annotators work independently. An adjudicator reviews disagreements without seeing model
output. Agreement is reported before adjudication.
