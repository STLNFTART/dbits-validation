# DBITS Equation Proof Summary

Generated from `run_dbits_validation.py` against Lightfoot (2025) `dbit_framework_corrected.pdf`.

## Discrete PL kernel

```
x_{t+1} = (1-δ) x_t + κ m_t
m_{t+1} = (1-λ) m_t + λ a_c x_t
J = [[1-δ, κ], [λ a_c, 1-λ]]
```

Spectral radius condition: ρ(J) < 1.

Sufficient box (Eq.107): δ,λ ∈ [0.2,0.4], |a_c κ| ≤ 0.1.

**Result:** 729/729 grid points inside box have ρ(J) ≤ 0.941.

## Lyapunov

V = α e_x² + β e_m² about (0,0). Along trajectories in the box, ΔV ≤ 0 (monotone decay).

## Gate families (§6.5)
All ten families received numerical certificates (neutral / contractive / bounded-gain as claimed).

## Continuous PL
Ė_PL = Θ E − λ E_PL; composite V = V0 + γ E_PL with design constraint Eq.140 → global asymptotic stability of stable plant demo.

## Primal-Heisenberg
C_PL(t) > 0 and bounded by αXαP/(λX+λP); Markov limit λ→∞ → C_PL→0.

## Scale
N=64 coupled dbits, 500 steps, mean energy decay ~10⁻⁸⁹.
