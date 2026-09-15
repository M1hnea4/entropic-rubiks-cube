# 🎲 Manim Entropic Rubik's Cube Simulator

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Manim](https://img.shields.io/badge/Manim-Math_Animation-blue?style=for-the-badge)
![Physics](https://img.shields.io/badge/Physics-Thermodynamics-FF6F00?style=for-the-badge)

A complex 3D physical simulation and mathematical visualization built using the **Manim** engine (created by 3Blue1Brown). The project models a closed thermodynamic system partitioned into a 3x3x3 grid (27 sub-cubes), tracking particle kinematics and calculating local spatial entropy in real-time.

### ⚙️ Computational Physics Engine
* **Elastic Kinematics:** Implements strict vector-based pairwise collision detection (`resolve_pairwise_collisions`) ensuring total kinetic energy is conserved when particles interact in 3D space.
* **Dynamic Spatial Entropy:** Uses Shannon's Information Entropy formula to calculate the disorder of particle distribution within each of the 27 individual sub-cubes. Each sub-cube is mathematically partitioned into 8 smaller micro-bins to evaluate probability distributions.
* **Procedural Data Visualization:** Seamlessly maps the calculated local entropy to a continuous color gradient, where Red indicates a highly ordered state (low entropy) and Blue indicates maximum disorder (high entropy)
* **Real-Time UI Updates:** Dynamically renders and updates 27 floating-point entropy trackers anchored to the camera frame, recalculating statistics on every sub-frame (`dt`) of the animation loop.

### 🎥 Visualization Concept
This engine is designed to visually demonstrate the Second Law of Thermodynamics, showing how kinetic agitation forces a system to transition from an ordered state to a statistically disordered (high entropy) state over time.
