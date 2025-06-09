import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# Soccer field dimensions (in meters)
field_length = 120
field_width = 80

# Create figure and axis with appropriate size
fig, ax = plt.subplots(figsize=(12, 8))

# Set the background color to green (representing the grass)
ax.set_facecolor('green')

# Create a grid for the heatmap
x = np.linspace(0, field_length, 100)
y = np.linspace(0, field_width, 100)
X, Y = np.meshgrid(x, y)

# Generate dummy heatmap data using Gaussian distributions
# Center Gaussian: higher activity in the middle of the field
Z1 = np.exp(-((X - 60)**2 / (2*30**2) + (Y - 40)**2 / (2*20**2)))
# Left goal Gaussian: higher activity near the left goal
Z2 = 0.8 * np.exp(-((X - 10)**2 / (2*10**2) + (Y - 40)**2 / (2*10**2)))
# Combine the two distributions and normalize
Z = Z1 + Z2
Z = Z / Z.max()  # Normalize to range [0, 1]

# Create a custom colormap: green (low) to yellow to red (high)
colors = ['green', 'yellow', 'red']
cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)

# Plot the heatmap with transparency to see field lines
heatmap = ax.imshow(Z, extent=[0, field_length, 0, field_width], origin='lower', cmap=cmap, alpha=0.7)

# Draw soccer field lines (white lines)
# Boundary lines
ax.plot([0, field_length], [0, 0], color='white', linewidth=2)
ax.plot([0, field_length], [field_width, field_width], color='white', linewidth=2)
ax.plot([0, 0], [0, field_width], color='white', linewidth=2)
ax.plot([field_length, field_length], [0, field_width], color='white', linewidth=2)
# Halfway line
ax.plot([field_length/2, field_length/2], [0, field_width], color='white', linewidth=2)
# Left penalty area (approximated)
ax.plot([0, 16.5], [20, 20], color='white', linewidth=2)
ax.plot([0, 16.5], [60, 60], color='white', linewidth=2)
ax.plot([16.5, 16.5], [20, 60], color='white', linewidth=2)
# Right penalty area (approximated)
ax.plot([field_length-16.5, field_length], [20, 20], color='white', linewidth=2)
ax.plot([field_length-16.5, field_length], [60, 60], color='white', linewidth=2)
ax.plot([field_length-16.5, field_length-16.5], [20, 60], color='white', linewidth=2)
# Goalposts (small white circles)
ax.plot(0, 36, 'wo', markersize=5)
ax.plot(0, 44, 'wo', markersize=5)
ax.plot(field_length, 36, 'wo', markersize=5)
ax.plot(field_length, 44, 'wo', markersize=5)

# Add a directional arrow to indicate the direction of play
ax.arrow(60, 70, 20, 0, head_width=2, head_length=2, fc='white', ec='white')

# Add a colorbar to represent activity intensity
cbar = fig.colorbar(heatmap, ax=ax, label='Activity Intensity')

# Customize the plot: remove axes and set title
ax.axis('off')
plt.title('Soccer Field Heatmap', fontsize=14, pad=20)

# Display the plot
plt.show()