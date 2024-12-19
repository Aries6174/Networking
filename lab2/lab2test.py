import numpy as np
import matplotlib.pyplot as plt

# Define individual sine terms
def term1(t, omega):
    return np.sin(omega * t)

def term2(t, omega):
    return (1/3) * np.sin(3 * omega * t)

def term3(t, omega):
    return (1/5) * np.sin(5 * omega * t)

# Parameters
omega = 2 * np.pi
t = np.linspace(0, 2, 1000)

# Compute the individual terms and the total sum
g1 = term1(t, omega)
g2 = term2(t, omega)
g3 = term3(t, omega)
gt = g1 + g2 + g3  # Total sum

# Plotting
plt.figure(figsize=(10, 6))

# Plot the first three sine terms combined
plt.plot(t, g1, label=r"$\sin(\omega t)$", color='blue')
plt.plot(t, g2, label=r"$\frac{1}{3}\sin(3\omega t)$", color='green')
plt.plot(t, g3, label=r"$\frac{1}{5}\sin(5\omega t)$", color='red')

# Add labels and legend
plt.title("Individual Sine Terms Combined")
plt.xlabel("Time (t)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

# Plot the total sum in a separate figure
plt.figure(figsize=(10, 6))
plt.plot(t, gt, label="Total g(t)", color='purple')
plt.title(r"$g(t) = \sin(\omega t) + \frac{1}{3}\sin(3\omega t) + \frac{1}{5}\sin(5\omega t)$")
plt.xlabel("Time (t)")
plt.ylabel("g(t)")
plt.grid(True)

# Show the plots
plt.show()
