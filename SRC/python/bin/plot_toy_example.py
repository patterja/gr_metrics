import csv
import numpy as np
import pandas as pd
import os.path as path
import seaborn as sns
import matplotlib.pyplot as plt
import gr50

# Read the data file.
base_path = path.join(path.dirname(path.abspath(__file__)), '..', '..')
input_path = path.join(base_path, 'OUTPUT', 'toy_example_output.tsv')
df = pd.read_csv(input_path, delimiter='\t')

# Adjust column names.
df.rename(columns={'GRvalue':'gr'}, inplace=True)
# Filter down to only a manageable subset of the experiments.
filters = (('time', 72), ('perturbation', 0), ('replicate', 1))
for column, value in filters:
    df = df[df[column] == value]
    del df[column]

# Compute the GR metrics from the data.
gr_metrics = gr50.gr_metrics(df)

# Produce a trellis plot showing the fitted curves and some of the metrics
# across the different cell lines and drugs.
sns.set(style="ticks")
grid = sns.FacetGrid(df, row="cell_line", col="agent", margin_titles=True)
grid.set(xscale="log")
grid.map(plt.plot, "concentration", "gr", lw=0, marker='o', ms=3)
x_min = df.concentration.min() / 10
x_max = df.concentration.max() * 10
fit_x = np.logspace(np.log10(x_min), np.log10(x_max))
for cell_line, row_axes in zip(grid.row_names, grid.axes):
    for agent, ax in zip(grid.col_names, row_axes):
        for m in gr_metrics[(gr_metrics.agent == agent) &
                            (gr_metrics.cell_line == cell_line)].itertuples():
            fit_y = gr50.logistic(fit_x, [m.gr_inf, m.ec50, m.slope])
            ax.hlines(0.5, x_min, x_max, '#a0a0a0', linestyles='dotted', lw=0.5)
            ax.hlines(m.gr_inf, x_min, x_max, '#ff00ff', linestyles='dashed', lw=0.5)
            ax.vlines(m.ec50, -1, 1, 'b', linestyles='dashed', lw=0.5)
            ax.vlines(m.gr50, -1, 1, 'g', linestyles='dashed', lw=0.5)
            ax.plot(fit_x, fit_y, 'r', lw=0.5)
grid.set(ylim=(-1, 1.1))
grid.fig.tight_layout(w_pad=1)
plt.show()
