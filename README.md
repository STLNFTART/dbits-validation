# DBITS Framework Validation

**Dynamic Quantum Bits (dbits)** — scale validation & equation-level proof certificates  
Donte Lightfoot (2025) · Source: `dbit_framework_corrected.pdf`

## Overall: **PASS** (6 / 6 certificates)

| # | Certificate | Equations | Status |
|---|---|---|---|
| 1 | Jacobian spectral radius / stability box | Eq.101–107 | PASS |
| 2 | Lyapunov V contraction | Eq.34, 41–42, 48 | PASS |
| 3 | Gate families 1–10 Lyapunov/contraction | §6.5 | PASS |
| 4 | Continuous PL composite Lyapunov | Eq.134–143 | PASS |
| 5 | Primal-Heisenberg C_PL positivity | Eq.150–161, Thm 9.3 | PASS |
| 6 | Scale multi-dbit (N=64, 500 steps) | Eq.65, 101, 107, Thm 6.7 | PASS |

### Key numbers
- Max ρ(J) inside Eq.107 box: **0.941** (< 1)
- Lyapunov V: monotone decay to ~0
- Scale energy decay ratio: **~2.3×10⁻⁸⁹**
- Content hash: `47ef7861e95ac866…`

### Stability box (Eq. 107)
```
δ, λ ∈ [0.2, 0.4]
|a_c κ| ≤ 0.1
```

## Claim boundary (from paper)
We validate engineered non-Markovian memory + Lyapunov control.  
**Not** claiming new fundamental physics or QM violations.

## Reproduce locally
```bash
cd C:\\Users\\stlta\\dbits-validation
python run_dbits_validation.py
# open site\\index.html
```

## Artifacts
- `site/index.html` — full interactive report with figures & animations  
- `artifacts/proofs/` — JSON certificates  
- `artifacts/figures/` — PNG scientific plots  
- `artifacts/animations/` — phase flow + Lyapunov GIFs  

## Deploy notes
- Vercel team `stlnftarts-projects` returned **402 account suspended** (billing).  
- Enable **GitHub Pages** on this repo (Settings → Pages → Deploy from `main` / root) after full site push, or open the local `site/index.html`.
