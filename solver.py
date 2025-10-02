import numpy as np
from itertools import product
from scipy.optimize import minimize
import json

class StoichiometrySolver:
    def build_skeleton_matrix(self, reactions, reactants, products, participants, participant_ids):
        n_reactants = len(reactants)
        n_products = len(products)
        skeleton_matrix = np.zeros(shape = (len(reactions), n_reactants + n_products))

        for primary_index,reaction in enumerate(reactions):
            reactants = reaction['reactants']
            products = reaction['products']

            for secondary_index in range(n_reactants + n_products):
                participant = participant_ids[secondary_index]
                if participant in reactants: skeleton_matrix[primary_index][secondary_index] = -1
                elif participant in products: skeleton_matrix[primary_index][secondary_index] = 1
        
        return skeleton_matrix.T

    def solve_reaction_algebraically(self, component_names, molar_masses, indices, skeleton_matrix, reaction_index):
        n_vars = len(component_names)

        required_signs = [skeleton_matrix[indices[i], reaction_index] for i in range(n_vars)]
        reactant_indices = [i for i, sign in enumerate(required_signs) if sign < 0]
        product_indices = [i for i, sign in enumerate(required_signs) if sign > 0]

        if not reactant_indices or not product_indices: return None

        max_coeff = 6
        best_solution = None
        best_error = float('inf')

        reactant_coeffs_range = [range(-max_coeff, -1)] * len(reactant_indices)
        product_coeffs_range = [range(1, max_coeff+1)] * len(product_indices)

        for reactant_coeffs in product(*reactant_coeffs_range):
            for product_coeffs in product(*product_coeffs_range):
                coeffs = [0] * n_vars
                for i, idx in enumerate(reactant_indices):
                    coeffs[idx] = reactant_coeffs[i]
                for i, idx in enumerate(product_indices):
                    coeffs[idx] = product_coeffs[i]

                mass_balance = sum(coeffs[i] * molar_masses[i] for i in range(n_vars))
                mass_error = abs(mass_balance)
                
                signs_correct = all(
                    (coeffs[i] < 0 and required_signs[i] < 0) or 
                    (coeffs[i] > 0 and required_signs[i] > 0) or 
                    (coeffs[i] == 0 and required_signs[i] == 0)
                    for i in range(n_vars)
                )
                
                if signs_correct and mass_error < best_error:
                    best_error = mass_error
                    best_solution = coeffs
                
                if signs_correct and mass_error < 0.01:
                    return coeffs
        
        if best_solution and best_error < 1.0:
            return best_solution
        
        return None

    def solve_reaction_optimization(self, component_names, molar_masses, indices, skeleton_matrix, reaction_index):
        n_vars = len(component_names)
        
        def objective(x):
            mass_error = sum(x[i] * molar_masses[i] for i in range(n_vars))
            
            sign_penalty = 0
            for i in range(n_vars):
                expected_sign = skeleton_matrix[indices[i], reaction_index]
                if expected_sign < 0 and x[i] > 0:  
                    sign_penalty += 1000 * abs(x[i])
                elif expected_sign > 0 and x[i] < 0:  
                    sign_penalty += 1000 * abs(x[i])
                elif expected_sign == 0 and abs(x[i]) > 0.001:  
                    sign_penalty += 1000 * abs(x[i])
            
            return mass_error**2 + sign_penalty
        
        x0 = []
        bounds = []
        for i in range(n_vars):
            sign = skeleton_matrix[indices[i], reaction_index]
            if sign < 0:  
                x0.append(-1.0)
                bounds.append((-10, -0.1))
            elif sign > 0:  
                x0.append(1.0)
                bounds.append((0.1, 10))
            else:  
                x0.append(0.0)
                bounds.append((0, 0))
        
        result = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')
        return result.x
    
    def solve_stoichiometry(self, reactants, products, reactions):
        participants = {}
        index = 0

        for reactant in reactants:
            participants[reactant['name']] = {
                'mass': reactant['molar_weight'],
                'molar_flow': -reactant['molar_flow'], 
                'id': index
            }
            index += 1

        for product in products:
            participants[product['name']] = {
                'mass': product['molar_weight'],
                'molar_flow': product['molar_flow'],
                'id': index
            }
            index += 1

        all_names = list(participants.keys())
        participant_ids = {i: name for i, name in enumerate(all_names)}
        molar_masses = {participant: participants[participant]['mass'] for participant in participants}

        skeleton_matrix = self.build_skeleton_matrix(reactions, reactants, products, participants, participant_ids)

        nu_matrix = np.zeros((len(all_names), len(reactions)))

        for r_idx, reaction in enumerate(reactions):
            participants_in_rxn = reaction['reactants'] + reaction['products']
            valid_participants = [p for p in participants_in_rxn if p in participants]
                    
            if len(valid_participants) < 2:
                continue
                
            participant_indices = []
            participant_names = []
            mw_values = []
            for comp in valid_participants:
                for pid, name in participant_ids.items():
                    if name == comp:
                        participant_indices.append(pid)
                        participant_names.append(name)
                        mw_values.append(molar_masses[name])
                        break
            
            nu_reaction = self.solve_reaction_algebraically(participant_names, mw_values, participant_indices, skeleton_matrix, r_idx)
            
            if nu_reaction is not None and self.check_mass_balance(nu_reaction, mw_values):
                for i, pid in enumerate(participant_indices):
                    nu_matrix[pid, r_idx] = nu_reaction[i]
            else:
                nu_reaction = self.solve_reaction_optimization(participant_names, mw_values, participant_indices, skeleton_matrix, r_idx)
                for i, pid in enumerate(participant_indices):
                    nu_matrix[pid, r_idx] = nu_reaction[i]
    
        mass_balance_errors = self.calculate_mass_balance_errors(nu_matrix, participants, participant_ids)

        nu_matrix = nu_matrix.T

        for row in range(nu_matrix.shape[0]):
            row_array = [abs(coeff) for coeff in nu_matrix[row]]
            max_val = max(row_array)
            nu_matrix[row] = nu_matrix[row]/max_val
 
        return {
            'success': True,
            'stoichiometric_coefficients': nu_matrix.T.tolist(),
            'mass_balance_errors': mass_balance_errors,
            'component_names': all_names
        }
    
    def check_mass_balance(self, coeffs, mw_values):
        mass_sum = sum(coeffs[i] * mw_values[i] for i in range(len(coeffs)))
        return abs(mass_sum) < 0.1
    
    def calculate_mass_balance_errors(self, nu_matrix, participants, participant_ids):
        mass_balance_errors = []
        n_reactions = nu_matrix.shape[1]
        
        molar_masses = {name: data['mass'] for name, data in participants.items()}
        
        for r_idx in range(n_reactions):
            mass_sum = 0
            for comp_idx in range(nu_matrix.shape[0]):
                comp_name = participant_ids[comp_idx]
                mass_sum += nu_matrix[comp_idx, r_idx] * molar_masses[comp_name]
            mass_balance_errors.append(abs(mass_sum))
        
        return mass_balance_errors
    
def solve_stoichiometry(reactants, products, reactions):
    solver = StoichiometrySolver()
    return solver.solve_stoichiometry(reactants, products, reactions)