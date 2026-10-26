#!/usr/bin/env python3
"""
delivery_viz.py - DISPOSABLE interactive view of delivery_sim.py. Not a production client.

You choose the element, the pattern and the first enemy (or the blast point for Mortar), press SPACE,
and watch the attack land. Every rule comes from the imported code, nothing is re-implemented:
  - targets: delivery_sim.targets (one hit per enemy, no jump range, directional + fallback)
  - Mortar:  delivery_sim.blast (enemies within MORTAR_R of the point you click; radius is a placeholder)
  - stacks:  chain_mr_sketch.advance, one stack per enemy, nothing carried between enemies

Run:  python3 delivery_viz.py "<magic dir>"
Keys: E W F L = element, S D T Q M = pattern, click = first enemy / blast point, SPACE = attack,
      R = reset stacks. Layout menu switches the test positions (and resets).
"""

import random
import sys
import tkinter as tk
from tkinter import ttk

import delivery_sim as ds
import travel_sim
from chain_mr_sketch import Chain, advance

ELEMENTS = ("earth", "water", "fire", "lightning")
COLORS = {"earth": "#8c6239", "water": "#3a78f0", "fire": "#ff7a1a", "lightning": "#f2dc2c",
          "Boil": "#ffb09a", "Steam": "#dfe3f0", "Plasma": "#ff40e0", "Char": "#5a2412",
          "Mudstorm": "#6b5a1e", "Grounding": "#46a35a"}
KEYS = {"e": ("element", "earth"), "w": ("element", "water"), "f": ("element", "fire"), "l": ("element", "lightning"),
        "s": ("pattern", "single"), "d": ("pattern", "double"), "t": ("pattern", "triple"),
        "q": ("pattern", "quad"), "m": ("pattern", "mortar")}
SCALE, W, H = 62, 1020, 660
STEP_MS = 650


def attack(board, field, element, pattern, pick, seed):
    """Run one attack on board (mutated). pick = enemy index, or an (x, z) point for Mortar.
    Returns hits [(enemy, before, after, kind, side)], the rolled side (None for Mortar) and fizzled count."""
    if pattern == "mortar":
        order = sorted(ds.blast(field, pick), key=lambda e: ds.dist(field[e], pick))
        sides, rolled, fizz = [None] * len(order), None, 0
    else:
        rolled = random.Random(seed).choice((-1, 1))  # the same first draw targets() makes from this seed
        order, fizz, follow = ds.targets(field, pick, pattern, random.Random(seed), ds.FALLBACK)
        sides = [None] + follow
    hits = []
    for e, side in zip(order, sides):
        before = board[e]
        board[e], _ = advance(before, element)
        hits.append((e, before, board[e], travel_sim.kind(before, board[e], element), side))
    return hits, rolled, fizz


def self_check():
    for name, field in ds.FIELDS.items():
        for pattern in ds.PATTERNS:
            for seed in range(100):
                for first in range(len(field)):
                    board = [Chain() for _ in field]
                    pick = field[first] if pattern == "mortar" else first
                    hits, rolled, fizz = attack(board, field, "fire", pattern, pick, seed)
                    want = ds.targets(field, first, pattern, random.Random(seed))[0]
                    assert sorted(h[0] for h in hits) == sorted(want) if pattern == "mortar" else [h[0] for h in hits] == want
                    assert all(h[2] == advance(Chain(), "fire")[0] for h in hits)
                    x0 = field[first][0]
                    rolled_pool = [e for e in range(len(field)) if e != first and
                                   ((field[e][0] - x0) * (rolled or 1) > 0 or field[e][0] == x0)]
                    if pattern != "mortar" and len(hits) > 1 and rolled_pool:
                        assert hits[1][4] == rolled, "displayed side roll differs from the one targets() used"
    print("self-check OK: viewer hits = delivery_sim.targets/blast; stacks = advance(); side roll shown = side used",
          file=sys.stderr)


class App:
    def __init__(self, root):
        self.root = root
        root.title("Delivery test - choose, then SPACE")
        root.configure(bg="#16161c")
        self.trail = []  # the last attack's arrows, kept until the next attack
        self.layout = tk.StringVar(value="wedge7")
        self.element = tk.StringVar(value="fire")
        self.pattern = tk.StringVar(value="triple")
        self.busy = False
        self.cast_no = 0
        self.canvas = tk.Canvas(root, width=W, height=H, bg="#16161c", highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="nsew")
        side = tk.Frame(root, bg="#202028", padx=10, pady=8)
        side.grid(row=0, column=1, sticky="nsew")
        lbl = dict(bg="#202028", fg="#e8e8f0", font=("Sans", 11))
        self.hero_lbl = tk.Label(side, text="", font=("Sans", 14, "bold"), bg="#202028", fg="#ffffff")
        self.hero_lbl.pack(anchor="w")
        tk.Label(side, text="Element (E W F L)", **lbl).pack(anchor="w", pady=(8, 0))
        for el in ELEMENTS:
            tk.Radiobutton(side, text=el.capitalize(), value=el, variable=self.element, takefocus=0,
                           selectcolor=COLORS[el], command=self.redraw, **lbl).pack(anchor="w")
        tk.Label(side, text="Pattern (S D T Q M)", **lbl).pack(anchor="w", pady=(8, 0))
        for p in ds.PATTERNS:
            tk.Radiobutton(side, text=p.capitalize() + (f"  (radius {ds.MORTAR_R} m, placeholder)" if p == "mortar" else ""),
                           value=p, variable=self.pattern, takefocus=0, selectcolor="#555",
                           command=self.pattern_changed, **lbl).pack(anchor="w")
        tk.Label(side, text="Layout (test positions)", **lbl).pack(anchor="w", pady=(8, 0))
        box = ttk.Combobox(side, textvariable=self.layout, values=list(ds.FIELDS), state="readonly", takefocus=0, width=14)
        box.bind("<<ComboboxSelected>>", lambda _: self.reset())
        box.pack(anchor="w")
        tk.Button(side, text="Reset stacks (R)", command=self.reset, takefocus=0).pack(anchor="w", pady=8)
        self.sel_lbl = tk.Label(side, text="", wraplength=300, justify="left", **lbl)
        self.sel_lbl.pack(anchor="w")
        self.log = tk.Text(root, width=44, height=20, bg="#101016", fg="#d8d8e0", font=("Monospace", 9),
                           wrap="word", takefocus=0)
        self.log.grid(row=1, column=1, sticky="nsew")
        for tag, col in {"head": "#ffffff", "react": "#7fe08a", "unres": "#f0a040", "fall": "#4fd8ff"}.items():
            self.log.tag_config(tag, foreground=col)
        self.canvas.bind("<Button-1>", self.click)
        root.bind_all("<space>", lambda _: self.fire() or "break")
        root.bind_all("<Key>", self.key)
        self.reset()

    # --- coordinates: x to the right, z toward the heroes (bottom of the screen)
    def px(self, p):
        return W / 2 + p[0] * SCALE, self.top + p[1] * SCALE

    def world(self, x, y):
        return (x - W / 2) / SCALE, (y - self.top) / SCALE

    def hero_xy(self, h):
        return W / 2 + (-4.5 + 3 * h) * SCALE, H - 40

    def reset(self):
        self.field = ds.FIELDS[self.layout.get()]
        self.board = [Chain() for _ in self.field]
        self.top = 95 - min(z for _, z in self.field) * SCALE  # farthest enemy just below the help line
        self.trail = []
        self.pick = 0 if self.pattern.get() != "mortar" else self.field[0]
        self.hero = 0
        self.log.delete("1.0", "end")
        self.write(f"Layout {self.layout.get()} - fresh stacks.\n", "head")
        self.redraw()

    def pattern_changed(self):
        if (self.pattern.get() == "mortar") != isinstance(self.pick, tuple):
            self.pick = self.field[self.pick] if not isinstance(self.pick, tuple) else min(
                range(len(self.field)), key=lambda e: ds.dist(self.field[e], self.pick))
        self.redraw()

    def key(self, ev):
        k = ev.keysym.lower()
        if k in KEYS and not self.busy:
            getattr(self, KEYS[k][0]).set(KEYS[k][1])
            self.pattern_changed()
        elif k == "r" and not self.busy:
            self.reset()

    def click(self, ev):
        if self.busy:
            return
        if self.pattern.get() == "mortar":
            self.pick = tuple(round(v, 2) for v in self.world(ev.x, ev.y))
        else:
            near = min(range(len(self.field)), key=lambda e: ds.dist(self.field[e], self.world(ev.x, ev.y)))
            if ds.dist(self.field[near], self.world(ev.x, ev.y)) < 0.8:
                self.pick = near
        self.redraw()

    def write(self, text, tag=None):
        self.log.insert("end", text, tag)
        self.log.see("end")

    # --- drawing
    def redraw(self, lit=()):
        c = self.canvas
        c.delete("all")
        c.create_text(12, 12, anchor="nw", fill="#9090a0", font=("Sans", 10),
                      text="Heroes stand at the bottom looking up the field. Left/right = screen left/right. "
                           "Click an enemy (or a ground point for Mortar), then SPACE.")
        c.create_line(W / 2, 40, W / 2, H - 70, fill="#26262e", dash=(2, 6))
        for h in range(4):
            x, y = self.hero_xy(h)
            col = COLORS[self.element.get()] if h == self.hero else "#444450"
            c.create_rectangle(x - 16, y - 16, x + 16, y + 16, fill=col, outline="")
            c.create_text(x, y + 26, text=f"Hero {h + 1}", fill="#c0c0c8", font=("Sans", 9))
        if self.pattern.get() == "mortar":
            x, y = self.px(self.pick)
            r = ds.MORTAR_R * SCALE
            c.create_oval(x - r, y - r, x + r, y + r, outline="#ff6060", dash=(6, 4), width=2)
            c.create_line(x - 8, y, x + 8, y, fill="#ff6060", width=2)
            c.create_line(x, y - 8, x, y + 8, fill="#ff6060", width=2)
            inside = set(ds.blast(self.field, self.pick))
        else:
            inside = set()
        for e, p in enumerate(self.field):
            x, y = self.px(p)
            ch = self.board[e]
            fill = COLORS.get(ch.state or (ch.elements[-1] if ch.elements else ""), "#3a3a44")
            if e == (self.pick if not isinstance(self.pick, tuple) else -1) or e in inside:
                c.create_oval(x - 31, y - 31, x + 31, y + 31, outline="#ffe14a", width=3)
            if e in lit:
                c.create_oval(x - 38, y - 38, x + 38, y + 38, outline="#ffffff", width=2)
            c.create_oval(x - 22, y - 22, x + 22, y + 22, fill=fill, outline="#9a9aa8" if not ch.closed else "#ff4040",
                          width=2)
            c.create_text(x, y, text=f"E{e + 1}", fill="#000" if fill in ("#f2dc2c", "#dfe3f0", "#ffb09a") else "#fff",
                          font=("Sans", 11, "bold"))
            stack = " ".join(el[0].upper() for el in ch.elements[-8:])
            more = "... " if len(ch.elements) > 8 else ""
            c.create_text(x, y + 34, text=more + stack, fill="#e0e0e8", font=("Monospace", 10))
            if ch.state or ch.closed:
                c.create_text(x, y + 50, text=(ch.state or "") + ("  [closed]" if ch.closed else ""),
                              fill=COLORS.get(ch.state, "#ff6060"), font=("Sans", 10, "bold"))
        for t in self.trail:
            self.draw_arrow(*t)
        el, pat = self.element.get(), self.pattern.get()
        self.hero_lbl.config(text=f"Hero {self.hero + 1}'s turn")
        where = (f"blast at ({self.pick[0]:.1f}, {self.pick[1]:.1f}) - {len(inside)} enemies inside"
                 if pat == "mortar" else f"first target E{self.pick + 1}")
        self.sel_lbl.config(text=f"Ready: {el.capitalize()} {pat.capitalize()}, {where}.\nPress SPACE.")

    def arrow(self, a, b, color, label, dashed=False):
        self.trail.append((a, b, color, label, dashed))
        self.draw_arrow(a, b, color, label, dashed)

    def draw_arrow(self, a, b, color, label, dashed):
        (x1, y1), (x2, y2) = a, b
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3, arrow="last", tags="trail",
                                dash=(8, 5) if dashed else None)
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10, text=label, fill=color, tags="trail",
                                font=("Sans", 10, "bold"))

    # --- attack
    def fire(self):
        if self.busy:
            return
        self.busy = True
        self.cast_no += 1
        el, pat, pick = self.element.get(), self.pattern.get(), self.pick
        hits, rolled, fizz = attack(self.board, self.field, el, pat, pick, f"viz:{self.cast_no}")
        hero = self.hero
        self.write(f"\nHero {hero + 1}: {el.capitalize()} {pat.capitalize()} ", "head")
        if pat == "mortar":
            self.write(f"blast at ({pick[0]:.1f}, {pick[1]:.1f}) hits {len(hits)} enem{'y' if len(hits) == 1 else 'ies'}\n", "head")
        else:
            self.write(f"on E{pick + 1}; side roll {'RIGHT' if rolled > 0 else 'LEFT'}\n", "head")
        # Snapshot the stacks before the attack so the animation can reveal them one hit at a time.
        shown = list(self.board)
        for e, before, *_ in hits:
            shown[e] = before
        real, self.board = self.board, shown
        self.redraw()
        self.animate(hits, rolled, fizz, el, pat, pick, hero, real, 0)

    def animate(self, hits, rolled, fizz, el, pat, pick, hero, real, i):
        if i == 0:
            self.trail = []
        if i == len(hits):
            if fizz:
                self.write(f"  {fizz} attack(s) fizzled: no enemy left on either side\n", "unres")
            self.board = real
            self.hero = (hero + 1) % 4
            self.busy = False
            self.redraw()
            return
        e, before, after, kind, side = hits[i]
        self.board[e] = after
        self.redraw(lit=(e,))
        color = COLORS[el]
        if pat == "mortar":
            src = self.px(pick)
            if i == 0:
                self.arrow(self.hero_xy(hero), src, color, "mortar")
            self.arrow(src, self.px(self.field[e]), color, f"{i + 1}")
            how = "in blast"
        else:
            if i == 0:
                src, how, dashed = self.hero_xy(hero), "first target (your pick)", False
            else:
                prev_side = hits[i - 1][4]
                fallback = side != rolled
                branch_start = i == 1 or side != prev_side
                src = self.px(self.field[pick if branch_start else hits[i - 1][0]])
                dashed = fallback
                how = (f"fallback {'RIGHT' if side > 0 else 'LEFT'} (rolled side empty)" if fallback and branch_start
                       else f"{'RIGHT' if side > 0 else 'LEFT'}, nearest" + (" (fallback side)" if fallback else ""))
            self.arrow(src, self.px(self.field[e]), "#4fd8ff" if dashed else color, f"{i + 1}", dashed)
        names = lambda ch: " > ".join(x.capitalize() for x in ch.elements[-2:])
        if kind == "convert":
            text, tag = f"{names(after)} = {after.state}" + (" (chain ends)" if after.closed else ""), "react"
        elif kind == "unresolved":
            text, tag = f"{names(after)}: no authored reaction (unresolved, old element replaced)", "unres"
        elif kind == "repeat":
            text, tag = f"{el.capitalize()} again: repeat closes the chain", "unres"
        else:
            text, tag = f"starts a chain with {el.capitalize()}" + (" (previous chain was closed)" if before.closed else ""), None
        self.write(f"  {i + 1}. E{e + 1} [{how}] ", "fall" if "fallback" in how else None)
        self.write(text + "\n", tag)
        self.root.after(STEP_MS, self.animate, hits, rolled, fizz, el, pat, pick, hero, real, i + 1)


def demo(app, script, out):
    """--demo: play scripted choices through the same handlers; save a screenshot after each attack (for checking)."""
    from PIL import ImageGrab

    def step(k):
        if app.busy:
            return app.root.after(100, step, k)
        if k:
            app.root.update()
            x, y = app.root.winfo_rootx(), app.root.winfo_rooty()
            ImageGrab.grab(bbox=(x, y, x + app.root.winfo_width(), y + app.root.winfo_height())).save(f"{out}_{k}.png")
        if k == len(script):
            print(f"WROTE {out}_1..{k}.png", file=sys.stderr)
            return app.root.destroy()
        el, pat, pick = script[k]
        app.element.set(el)
        app.pattern.set(pat)
        app.pick = pick
        app.fire()
        app.root.after(100, step, k + 1)
    app.root.after(500, step, 0)


if __name__ == "__main__":
    self_check()
    root = tk.Tk()
    app = App(root)
    if "--demo" in sys.argv:
        demo(app, [("earth", "triple", 3), ("water", "triple", 3), ("fire", "double", 0),
                   ("lightning", "triple", 6), ("fire", "mortar", (0.0, -2.2))], sys.argv[sys.argv.index("--demo") + 1])
    root.mainloop()
