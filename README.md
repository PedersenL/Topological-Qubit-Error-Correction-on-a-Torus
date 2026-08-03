# Topological Qubit Error Correction on a Torus 

This repository contains a simulation framework for analysis on topological quantum error correction on a torus, comparing toric codes with different stabilizers under biased noise models.

This project was done as part of a Quantum Ideas Factory at the Abbe Center of Photonics and while the code was written by myself (with AI assistance on the data-analysis), the presentation was made with the help of Rose Lambert-hartmann. We are thankful for the assistance of our advisor Elena.

---

## Repository Structure

* [`toric_code.py`](file:///c:/Users/kimpe/OneDrive/Documents/DTU Fag/6th Semester/Topological-Qubit-Error-Correction-on-a-Torus/toric_code.py): The core simulation library containing all helper functions (system startup, stabilizer measurements, syndrome graphing, decoding with MWPM, logical loop checkers, parameter sweeps, and S-curve plotting).
* [`simulation_analysis.ipynb`](file:///c:/Users/kimpe/OneDrive/Documents/DTU Fag/6th Semester/Topological-Qubit-Error-Correction-on-a-Torus/simulation_analysis.ipynb): The main analysis notebook, which imports the modular functions from `toric_code.py` to run tests and analyze thresholds under standard vs. XZZX bases.

---

## Setup & Running the Code

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PedersenL/Topological-Qubit-Error-Correction-on-a-Torus.git
   cd Topological-Qubit-Error-Correction-on-a-Torus
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Explore the Notebooks:**
   Open the Jupyter environment and run `simulation_analysis.ipynb`:
   ```bash
   jupyter notebook
   ```
