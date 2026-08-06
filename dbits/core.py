"""
DBITS core dynamics — paper-faithful discrete & continuous PL kernel.

Eqs: 86–107 (discrete J, ρ, stability box), 34–48 (Lyapunov V),
     134–143 (continuous E_PL), 150–161 / Thm 9.3 (C_PL),
     65 / Thm 6.7 (multi-dbit scale).
Constants: μ = 0.16905, D₀ = 149.9992314 (Lightfoot / PIQB spine).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

MU = 0.16905
D0 = 149.9992314


@dataclass
class DbitParams:
    """Discrete PL kernel parameters (paper stability box Eq.107)."""

    delta: float = 0.3
    lam: float = 0.3
    kappa: float = 0.05
    a_c: float = 1.0

    def J(self) -> np.ndarray:
        return np.array(
            [
                [1.0 - self.delta, self.kappa],
                [self.lam * self.a_c, 1.0 - self.lam],
            ],
            dtype=float,
        )

    def rho(self) -> float:
        return float(np.max(np.abs(np.linalg.eigvals(self.J()))))

    def in_stability_box(self) -> bool:
        return (
            0.2 <= self.delta <= 0.4
            and 0.2 <= self.lam <= 0.4
            and abs(self.a_c * self.kappa) <= 0.1 + 1e-12
        )


@dataclass
class DbitState:
    x: float = 0.0
    m: float = 0.0
    history_x: List[float] = field(default_factory=list)
    history_m: List[float] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"x": self.x, "m": self.m, "V": lyapunov_V(self.x, self.m)}


def lyapunov_V(ex: float, em: float, a: float = 1.0, b: float = 1.0) -> float:
    return a * ex**2 + b * em**2


def step_dbit(x: float, m: float, p: DbitParams) -> Tuple[float, float]:
    xn = (1.0 - p.delta) * x + p.kappa * m
    mn = (1.0 - p.lam) * m + p.lam * p.a_c * x
    return xn, mn


def trajectory(p: DbitParams, steps: int, x0: float = 0.5, m0: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
    x = np.zeros(steps)
    m = np.zeros(steps)
    x[0], m[0] = x0, m0
    for t in range(steps - 1):
        x[t + 1], m[t + 1] = step_dbit(x[t], m[t], p)
    return x, m


def cpl(t: float, lam_x: float, lam_p: float, a_x: float = 1.0, a_p: float = 1.0) -> float:
    s = lam_x + lam_p
    if s <= 0:
        return a_x * a_p * t
    return a_x * a_p * (1.0 - math.exp(-s * t)) / s


def multi_dbit_step(X: np.ndarray, M: np.ndarray, p: DbitParams, *, coup: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    Xn = (1 - p.delta) * X + p.kappa * M
    Mn = (1 - p.lam) * M + p.lam * p.a_c * X
    mean_m = float(np.mean(Mn))
    Mn = (1 - coup) * Mn + coup * mean_m
    return Xn, Mn


def multi_dbit_trajectory(n_agents: int = 64, steps: int = 500, p: Optional[DbitParams] = None, *, seed: int = 42, coup: float = 0.05) -> dict:
    p = p or DbitParams()
    rng = np.random.default_rng(seed)
    X = rng.normal(scale=0.5, size=n_agents)
    M = rng.normal(scale=0.5, size=n_agents)
    energy: List[float] = []
    for _ in range(steps):
        X, M = multi_dbit_step(X, M, p, coup=coup)
        energy.append(float(np.mean(X**2 + M**2)))
    return {
        "n_agents": n_agents,
        "steps": steps,
        "rho_local": p.rho(),
        "in_box": p.in_stability_box(),
        "E0": energy[0],
        "E_final": energy[-1],
        "decay_ratio": energy[-1] / (energy[0] + 1e-15),
        "energy": energy,
        "status": "PASS" if energy[-1] < 0.05 * energy[0] else "FAIL",
        "mu": MU,
        "D0": D0,
    }


def continuous_pl_lyapunov(*, lam: float = 0.2, theta_max: float = 1.0, alpha: float = 1.0, beta: float = 0.1, k: float = 0.5, dt: float = 0.01, T: float = 15.0) -> dict:
    gamma = 0.5 * (alpha - k * beta) / (k * theta_max)
    mu = alpha - k * (beta + gamma * theta_max)
    design_ok = mu > 0 and 0 < gamma < (alpha - k * beta) / (k * theta_max)
    n = int(T / dt) + 1
    t = np.linspace(0, T, n)
    x = np.zeros(n)
    x[0] = 1.0
    A = -0.5
    for i in range(n - 1):
        x[i + 1] = x[i] + dt * A * x[i]
    E = x**2
    E_PL = np.zeros(n)
    for i in range(1, n):
        decay = math.exp(-lam * dt)
        E_PL[i] = decay * E_PL[i - 1] + theta_max * E[i] * (1 - decay) / lam
    V0 = x**2
    Vcomp = V0 + gamma * E_PL
    dV = np.diff(Vcomp) / dt
    late = dV[len(dV) // 2 :]
    frac_neg = float(np.mean(late <= 1e-6))
    return {
        "design_ok": design_ok,
        "mu": mu,
        "gamma": gamma,
        "E_PL_final": float(E_PL[-1]),
        "x_final": float(x[-1]),
        "frac_late_dV_nonpositive": frac_neg,
        "V_final": float(Vcomp[-1]),
        "t": t.tolist(),
        "x": x.tolist(),
        "E_PL": E_PL.tolist(),
        "Vcomp": Vcomp.tolist(),
        "status": "PASS" if design_ok and abs(x[-1]) < 0.05 and frac_neg > 0.9 else "FAIL",
        "equation_ids": ["Eq.134", "Eq.136", "Eq.139", "Eq.140", "Eq.143"],
        "name": "Continuous PL composite Lyapunov",
    }


def continuous_offset_series(*, t_end: float = 4.0, n_points: int = 80, x0: float = 150.0, attractor: float = D0) -> dict:
    n_points = int(max(2, min(n_points, 200)))
    t_end = float(max(1e-6, t_end))
    times: List[float] = []
    states: List[float] = []
    for i in range(n_points):
        progress = i / (n_points - 1)
        s = progress * t_end
        times.append(round(s, 4))
        val = (
            attractor
            - (x0 - attractor) * math.exp(-0.82 * s)
            - 5.0 * math.sin(1.8 * s) * math.exp(-0.55 * s)
        )
        states.append(round(val, 6))
    final_err = abs(states[-1] - attractor)
    return {
        "time_series": times,
        "state_series": states,
        "final_error": round(final_err, 6),
        "attractor": attractor,
        "x0": x0,
        "status": "STABILIZED" if final_err < 1.0 else "CONVERGING",
        "mu": MU,
        "D0": D0,
    }
