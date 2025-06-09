import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mplsoccer import Pitch

# Generate synthetic player position data
np.random.seed(42)
x_positions = np.random.uniform(0, 100, 200)  # X-coordinates (0 to 100)
y_positions = np.random.uniform(0, 100, 200)  # Y-coordinates (0 to 100)

# Create pitch
pitch = Pitch(pitch_type='statsbomb', line_color='black')
fig, ax = pitch.draw(figsize=(10, 6))

# Plot heatmap
sns.kdeplot(x=x_positions, y=y_positions, shade=True, cmap="Reds", alpha=0.6, ax=ax)

# Show plot
plt.title("Player Heatmap - Ball Touches")
plt.show()
