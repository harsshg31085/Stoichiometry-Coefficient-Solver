# Stoichiometry Solver

## 1. Installation

### If Git is not installed:
1. Download the zip file from the **"Code"** button on GitHub.
2. Unzip it into your desired directory.
3. Open **Terminal** or **PowerShell** in the folder containing `.gitignore` and `README.md`.
4. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Run the program using:

    ```bash
    python gui.py
    ```

### If Git is installed:
1. In your desired directory, open terminal and run:

    ```bash
    git clone https://github.com/harsshg31085/Stoichiometry-Coefficient-Solver
    ```

2. Navigate inside the `Stoichiometry-Coefficient-Solver` folder.
3. Follow the steps listed above for running the program.


## 2. Usage

### Information Input
- Run the **`gui.py`** file in the `Stoichiometry` folder (Using the command prompt).
- If the program runs correctly, you will see an interface titled **Chemical Stoichiometry Manager**.
- Enter your:
  - Total mass flow  
  - Reactants  
  - Products  
  - Reactions  
  in their respective fields, or import them from a JSON file (**Load from JSON**).
- You can **Save to JSON** to store your entered data for future use.
- The **Stoichiometry Solver** tab will display information about product flows and total product flow.

### Solving for Coefficients
- Click on **Solve Stoichiometry**.
- The **Stoichiometry Solver** tab will show the calculated stoichiometric coefficients.
- Results can be:
  - Copied to clipboard  
  - Saved to a `.txt` file  

### Control Buttons
- **Save to JSON** → Saves current data into a JSON file of your choice.  
- **Load from JSON** → Loads data from a JSON file.  
- **Calculate All** → Recalculates all molar flows and mass flows.  
- **Clear All** → Clears all the data in the reactant and product sections.  

---

## 3. Solving Process

- The problem is framed as an **optimization problem**:  
  Goal → Reduce the difference between **initial mass** (before reaction) and **final mass** (after reaction).

- Solving is done **individually for each reaction**.  
  Assumption → Optimizing each reaction individually optimizes the whole system (valid in most cases).

### Steps:
1. **Exact (Algebraic) Solution**  
   - Attempted first, but generally not possible.  
   - Always results in some error.

2. **Numerical Solution (Fallback)**  
   - Used if algebraic error is too high.  
   - Slower but guarantees results.  
   - Objective: Minimize  
     $\| \nu \cdot \varepsilon - \Delta n \|_2$  
     where:  
     - **ν** = array of stoichiometric coefficient vectors  
     - **ε** = vector of extent of each reaction  
     - **Δn** = vector of observed molar flow
     - **$\| a \|_2$** = L2 norm of vector $a$

3. **Error Handling & Constraints**
   - Numerical solutions may yield:
     - Negative coefficients  
     - Coefficients for components not present in the reaction  
   - Fixed by:  
     - Adding **large penalties** for incorrect signs  
     - Preventing assignment of coefficients to non-reaction components  

4. **Implementation**
   - Minimization algorithm carried out using **SciPy** (v1.16.2).  
---
## 4. JSON File Format
### A valid JSON file will contain the following information
1. **Total Reactant Mass**: float
2. **List of Reactants and Products**: List[dict]
3. **List of Reactions**: List[dict]

### A sample JSON file
```bash
{
	"total_reactant_mass": 112000.0,
	"reactants": [
		{
			"name": "Reactant_1",
			"mole_fraction": 0.210810810810811,
			"molar_weight": 123.1,
			"mass_flow": 23610.81081081083,
			"molar_flow": 191.80187498627808
		},
		...other reactants...
	],
	"products": [
		{
			"name": "Product_1",
            "mole_fraction": 0.55,
            "molar_weight": 234.0,
            "mass_flow": 61250.20280449647,
            "molar_flow": 261.7530034380191
		},
		...other products...
	],
	"reactions": [
		{
			"name": "Reaction 1",
            "reactants": [
                "Comp_r1",
                "Comp_r2",
                "Comp_r3",
                "Comp_r4"
            ],
            "products": [
                "Prod1",
                "Prod2"
            ]
		},
		...other reactions...
	]
}
```
