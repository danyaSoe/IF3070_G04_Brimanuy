import json
import numpy as np
import matplotlib.pyplot as plt

with open("output/output_local/sa/seed_2/result.json") as f:   # sesuaikan nama file
    data = json.load(f)

v = np.array(data["history"])
it = np.arange(len(v))
d = np.diff(v)

w = 100
kernel = np.ones(w) / w
accepted = np.convolve(d != 0, kernel, mode="valid")   # proporsi move yang mengubah state
worse = np.convolve(d < 0, kernel, mode="valid")       # proporsi move buruk yang diterima

fig, ax = plt.subplots(1, 2, figsize=(13, 4))

ax[0].plot(it, v, lw=0.8)
ax[0].set(title="SA seed=1: nilai objective per iterasi",
          xlabel="Iterasi asli", ylabel="Objective")

ax[1].plot(accepted, label="state berubah")
ax[1].plot(worse, label="move buruk diterima")
ax[1].set(title=f"Rasio per jendela {w} iterasi",
          xlabel="Iterasi", ylabel="Proporsi")
ax[1].legend()

for a in ax:
    a.grid(True)
plt.tight_layout()
plt.savefig("output/output_local/sa/seed_2/sa_seed2_history.png", dpi=200)