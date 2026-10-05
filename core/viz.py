import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from .models import OUT
from .objective import evaluate, is_feasible

def draw_state(problem, state, title="", save=None):
    ns = len(problem.ships)
    fig, axes = plt.subplots(1, ns + 1, figsize=(5 * (ns + 1), 7))
    axes = axes if ns + 1 > 1 else [axes]
    cmap = plt.get_cmap("tab20")
    for s, ship in enumerate(problem.ships):
        ax = axes[s]
        ax.set_xlim(0, ship.w); ax.set_ylim(ship.l, 0); ax.set_aspect("equal")
        ax.set_xticks(range(ship.w + 1)); ax.set_yticks(range(ship.l + 1)); ax.grid(True)
        load = 0
        for i, (sh, x, y, o) in enumerate(state):
            if sh != s: continue
            fw, fl = problem.footprint(i, o)
            ax.add_patch(Rectangle((x, y), fw, fl, facecolor=cmap(i % 20), edgecolor="k", alpha=.8))
            ax.text(x + fw/2, y + fl/2, problem.vehicles[i].id, ha="center", va="center", fontsize=8)
            load += problem.vehicles[i].weight
        ax.set_title(f"{ship.id} | berat {load}/{ship.max_capacity}")
    out = [problem.vehicles[i] for i, p in enumerate(state) if p[0] == OUT]
    axes[-1].axis("off")
    axes[-1].text(0, 1, "Di luar kapal:\n" + "\n".join(
        f"{v.id} ({v.w}x{v.l}, fee {v.fee}, berat {v.weight})" for v in out), va="top")
    fig.suptitle(f"{title} | value={evaluate(problem, state):.1f} | valid={is_feasible(problem, state)}")
    fig.savefig(save, dpi=120, bbox_inches="tight") if save else plt.show()
    plt.close(fig)

def plot_curves(curves: dict, title, xlabel, ylabel, save=None):
    plt.figure(figsize=(8, 4))
    for label, ys in curves.items():
        plt.plot(ys, label=label)
    plt.title(title); plt.xlabel(xlabel); plt.ylabel(ylabel); plt.legend(); plt.grid(True)
    plt.savefig(save, dpi=120, bbox_inches="tight") if save else plt.show()
    plt.close()