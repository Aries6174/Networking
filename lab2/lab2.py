import numpy as np
import matplotlib.pyplot as plt

def cosSeries(t, omega, N):
    #The Equation
    result = np.zeros_like(t)
    for n in range(1, 2*N, 2):
        result += (1 / n**2) * np.cos(n * omega * t)
    return (8 / np.pi**2) * result


def plot_cosSeries():
    N = int(input("Enter the number of sine terms in the series (N): "))

    omega = 2 * np.pi
    sample_rate = 48000
    duration = 1

    t = np.linspace(0, duration, int(sample_rate * duration))
    y = cosSeries(t, omega, N)

    #Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(t, y, label=f"cosine series with N = {N} terms")
    plt.title(r"$y(t) = \frac{8}{\pi^2} \left( \cos(\omega t) + \frac{1}{9} \cos(3\omega t) + \dots + \frac{1}{N^2} \cos(N\omega t) \right)$")
    plt.xlabel("Time (t)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()

    #Show
    plt.show()

plot_cosSeries()
