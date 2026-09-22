# C4 — An ESM-independent specificity axis (roadmap F1–F3)

**Why it is needed.** C1–C3 show that ΔΔG_bind cannot be learned from the available data for SH3.
The atlas binding flag (B3) is therefore zero-shot ESM-2, and **both atlas axes derive from ESM**. As
long as that is true, the core question — do folding and binding effects separate? — cannot be
tested. This program tries the one route the data allows.

## Data
- **154 phage-display PWMs** for human SH3 domains (Teyra et al. 2017), linked to their exact domain
  sequences through supplementary Table S2.
- Values are shipped as probability × 20 per column and are normalised on load.

## Method
1. **Target: an alignment-free specificity profile.**
   - Each PWM is summarised as an information-weighted amino-acid preference vector (20 numbers).
   - PWMs have different widths and no common peptide frame, so position-by-position comparison
     across domains is impossible.
   - A domain with two PWMs gets their average.
2. **Model:** ridge regression from the domain's mean ESM-2 embedding to the profile, in
   centred-log-ratio space so predictions stay valid probability vectors. The ridge strength is
   chosen by inner cross-validation.
3. **Test:** whole **clusters of related domains** (≥ 40 % identity) are held out, so a paralogue
   cannot give the answer away.
4. **Baselines:**
   - the training-average profile (all SH3s prefer proline);
   - the profile of the most similar training domain.
5. **Metric:** the *centred* correlation (predicted minus average vs observed minus average), so the
   shared proline preference does not inflate it. Jensen–Shannon distance is reported as well.

## Pre-specified decision rule
The axis is **validated** only if:
- the 95 % bootstrap CI of the median centred r lies above zero, **and**
- the model beats the average profile on a sign test with p < 0.05.

## If validated
- **Score:** rewiring = Jensen–Shannon distance between the predicted wild-type and mutant profiles.
  The mutant profile comes from a fresh ESM-2 pass over each mutant domain sequence.
- **Two checks:**
  - Is rewiring higher at the peptide interface? It should be, if it means anything.
  - How strongly does it correlate with predicted folding damage? A low correlation means a
    genuinely separate axis.

## If not validated
The scores are written, labelled *not validated*, and no rewiring claim is made. The honest
conclusion is then that 154 profiles are too few to learn specificity. That is a data limit,
reported like the binding result.

## Honest limits
- The model still uses ESM-2 **embeddings as input**. What is independent is the **target**
  (experimental specificity), not the representation.
- A single substitution changes a mean-pooled embedding only slightly, so rewiring scores will be
  small and noisy.
- Phage display reports preference among binders only; there are no non-binders.
