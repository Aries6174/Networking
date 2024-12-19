import numpy as np
import matplotlib.pyplot as plt

def sinSeries(t, omega, N):
    # The updated equation: g(t) = sin(omega * t) + (1/3)sin(3omega * t) + (1/5)sin(5omega * t) + ...
    result = np.zeros_like(t)
    for n in range(1, 2*N, 2):  # Loop over odd values of n: 1, 3, 5, ...
        result += (1 / n) * np.sin(n * omega * t)
    return result

def plot_sinSeries():
    N = int(input("Enter the number of sine terms in the series (N): "))

    omega = 2 * np.pi  # Angular frequency (assuming frequency = 1 Hz)
    sample_rate = 48000  # Sampling rate of 48 kHz
    duration = 1  # Duration of 1 second

    t = np.linspace(0, duration, int(sample_rate * duration))  # Time array
    y = sinSeries(t, omega, N)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(t, y, label=f"Sine series with N = {N} terms")
    
    # Update the plot title to reflect the sine series equation
    plt.title(r"$g(t) = \sin(\omega t) + \frac{1}{3}\sin(3\omega t) + \frac{1}{5}\sin(5\omega t) + \dots$")
    
    plt.xlabel("Time (t)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    # Show the plot
    plt.show()

# Call the function to execute
plot_sinSeries()
