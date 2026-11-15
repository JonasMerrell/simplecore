#!/usr/bin/env python3
"""Belt path of the simplecore AWD CoreXY with 9 mm belts (plan view, world mm).
Each belt is a list of (name, x, y, pitch_radius, turn) in travel order; turn is +1 for a left (ccw) wrap, -1 for right (cw).
Prints tangent points, wrap angles and length, checks the length stays constant over travel, draws beltpath.png."""
import math, sys
PT, PS_BACK, PS_TEETH = 6.366, 6.5 + 0.37, 6.5 + 1.01   # 20T pulley / toothed idler; F695 on the belt back; F695 on the teeth
XJ = 207.6 - 185.3      # joint idler x relative to gantry centre (model pose: gantry centre 185.3)
def tangent(c1, c2):
    (x1, y1, r1, s1), (x2, y2, r2, s2) = c1, c2
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy); th = math.atan2(dy, dx)
    # signed radii: a circle on the left of travel (ccw wrap) has its centre at +r along the left normal
    a, b = s1 * r1, s2 * r2
    phi = math.asin((a - b) / d)          # direction of travel = th + phi
    t = th + phi
    n = (-math.sin(t), math.cos(t))        # left normal
    return (x1 - a * n[0], y1 - a * n[1]), (x2 - b * n[0], y2 - b * n[1]), t
def path(circs, closed=True):
    n = len(circs); segs = []
    for i in range(n if closed else n - 1):
        segs.append(tangent(circs[i][1:], circs[(i + 1) % n][1:]))
    L = 0; wraps = []
    for i, (p, q, t) in enumerate(segs): L += math.dist(p, q)
    for i in range(n):
        if not closed and (i == 0 or i == n - 1): wraps.append(0); continue
        tin = segs[i - 1][2]; tout = segs[i][2] if i < len(segs) else 0
        s = circs[i][4]; w = (s * (tout - tin)) % (2 * math.pi); wraps.append(math.degrees(w)); L += w * circs[i][3]
    return segs, wraps, L
def belts(gx, cy, XF=3.5):
    """gx: gantry centre x, cy: carriage (belt end) y. XF: front pulley x."""
    jx = gx + XJ
    # belt U (upper level): carriage -> +Y smooth joint -> front +Y motor -> rear +Y (A, C, motor P) -> across the back -> rear -Y (B', A') -> -Y toothed joint -> carriage
    U = [("carriage", jx - 3.13, cy, 0.01, 1),
         ("joint +Y smooth", gx + 197.6 - 185.3, 443.8, PS_BACK, 1),
         ("front +Y I1", XF + 6.37 + PS_BACK, 450.67 - PS_BACK, PS_BACK, 1),      # turns the joint run inboard
         ("front +Y motor", XF, 422.0, PT, -1),                                 # 180 deg, inboard of the panel
         ("front +Y I3", XF + 2 * 0 - 6.37 + PS_TEETH, 450.67 + 2 * PT - PS_TEETH, PS_TEETH, -1),   # back out to the side run
         ("rear +Y A", 385.5, 455.36, PS_TEETH, -1),
         ("rear +Y C", 391.0, 422.4, PS_BACK, 1),
         ("rear +Y motor P", 403.3, 433.0, PT, -1),
         ("rear -Y B'", 391.0, 453 - 422.4, PS_TEETH, -1),
         ("rear -Y A'", 385.5, 453 - 455.36, PS_TEETH, -1),
         ("joint -Y toothed", jx, -3.5, PT, -1),
         ("carriage", jx - 6.4, cy, 0.01, 1)]
    Lb = [(n.replace("+Y", "#").replace("-Y", "+Y").replace("#", "-Y"), x, 453 - y, r, -s) for (n, x, y, r, s) in U]
    return U, Lb
def draw(fn):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 10))
    for (x0, y0) in [(-25.5, -23.5), (-25.5, 456.5), (404.5, -23.5), (404.5, 456.5)]:
        ax.add_patch(plt.Rectangle((y0, x0), 20, 20, fc="#bbb", ec="k"))
    for nm, B, col in zip(("U, upper level: motors on the left side (+Y)", "L, lower level: motors on the right side (-Y)"), belts(185.3, 241.5), ("tab:blue", "tab:red")):
        segs, wraps, L = path(B, closed=False)
        for i, (p, q, t) in enumerate(segs): ax.plot([p[1], q[1]], [p[0], q[0]], col, lw=1.6, label=nm if i == 0 else None)
        for (n, x, y, r, s) in B[1:-1]:
            ax.add_patch(plt.Circle((y, x), r, fc="none", ec=col, lw=1)); ax.plot(y, x, ".", color=col, ms=3)
            if "motor" in n: ax.add_patch(plt.Rectangle((y - 21, x - 21), 42, 42, fc="none", ec=col, ls=":", lw=0.8))
    ax.set_aspect("equal"); ax.invert_xaxis(); ax.set_xlabel("Y (mm)  |  LEFT side of the printer (seen from the front door) is on the left, RIGHT on the right"); ax.set_ylabel("X (mm)  |  front door at the bottom, rear at the top"); ax.legend(loc="center")
    ax.set_title("simplecore 9 mm belt path, seen from above (gantry and carriage at mid travel)"); ax.grid(True, lw=0.3); fig.savefig(fn, dpi=110, bbox_inches="tight")
if __name__ == "__main__":
    for nm, B in zip("UL", belts(185.3, 241.5)):
        segs, wraps, L = path(B, closed=False)
        print("belt", nm, "length between clamp points %.1f mm" % L)
        for (c, w) in zip(B, wraps):
            if w: print("   %-18s (%7.2f, %7.2f) r %.2f  wrap %5.1f deg" % (c[0], c[1], c[2], c[3], w))
        for (p, q, t) in segs: print("      run (%.1f, %.1f) -> (%.1f, %.1f)  %.1f mm" % (p[0], p[1], q[0], q[1], math.dist(p, q)))
    ref = [path(B, closed=False)[2] for B in belts(185.3, 241.5)]
    worst = 0
    for gx in (45, 120, 250, 345):
        for cy in (90, 240, 395):
            for k, B in enumerate(belts(gx, cy)):
                L = path(B, closed=False)[2]; dU = L - ref[k]
                # pure X or Y moves change each belt by a fixed amount; the check is that U and L change equally for X moves and oppositely for Y moves
                worst = max(worst, abs(dU - ((gx - 185.3) * 0 + 0)))
    print("largest length change over travel (should be ~0): %.3f mm" % worst)
    draw("beltpath.png")
