# C1 — Binding across domains (Stage 3)

**Question.** If a binding head is trained on two ddPCA domains, does it predict the third?

**Set-up.**
- *Design:* leave-one-domain-out over GRB2-SH3, PSD95-PDZ3 and GB1.
- *Model:* a small head (64-unit hidden layer) on a 64-component PCA of the frozen features. It is
  kept small because ~2,800 measurements against a 650M-parameter encoder would be memorised.

**Why it could not work.** To predict GRB2-SH3, the model learns from a PDZ domain (which reads
C-terminal peptides) and from GB1 (which binds the folded surface of IgG). Neither shares the SH3
binding mode, so there is nothing to transfer. This is the first step of the reasoning, not a test of
SH3 biology.

## Two versions
- **original** — the Stage 3 code exactly. On re-checking, it **used the held-out domain as its
  early-stopping set**: training stopped at the epoch that scored best on the test data. That is
  leakage, and it can only flatter the result.
- **corrected** — early stopping on an inner split of the training domains, with the
  variance-floored scaler and whitened PCA that Stage 3b introduced.

## Expected result (original)
GRB2-SH3 ρ +0.097, PSD95-PDZ3 +0.112, GB1 −0.090. Zero-shot ESM-2 is better on both domains that
matter. The corrected version is expected to be no better.
