import re
from itertools import permutations, product

class LogicPuzzleCSP:
    def __init__(self, data_file, clues_file):
        self.attributes, self.values = self.parse_data_file(data_file)
        self.clues = self.parse_clues_file(clues_file)
        self.variables = self.initialize_variables()
        self.assignments = {f'subject{i}': {} for i in range(4)}

    def parse_data_file(self, data_file):
        attributes = []
        values = {}

        with open(data_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                attribute = parts[0]
                attributes.append(attribute)
                values[attribute] = parts[1:]
        
        return attributes, values

    def parse_clues_file(self, clues_file):
        clues = []
        
        with open(clues_file, 'r') as f:
            for line in f:
                clues.append(line.strip())
        
        return clues

    def initialize_variables(self):
        # Define initial domains for each subject and each attribute
        subjects = {f'subject{i}': {} for i in range(4)}
        
        for subject in subjects:
            for attribute in self.attributes:
                subjects[subject][attribute] = set(self.values[attribute])
        
        return subjects

    def solve(self):
        # Generate all possible assignments
        domains = [list(product(*[self.values[attr] for attr in self.attributes]))]
        for assignment in domains[0]:
            for i, attr_values in enumerate(assignment):
                for j, attr in enumerate(self.attributes):
                    self.assignments[f'subject{i}'][attr] = attr_values[j]
            if self.apply_constraints():
                return self.assignments
        return None

    def apply_constraints(self):
        for clue in self.clues:
            if "then" in clue:
                if not self.apply_if_then_constraint(clue):
                    return False
            elif ">" in clue or "<" in clue:
                if not self.apply_inequality_constraint(clue):
                    return False
            elif "are all different" in clue:
                if not self.apply_different_constraint(clue):
                    return False
            elif "one of" in clue:
                if not self.apply_one_of_constraint(clue):
                    return False
        return True

    def apply_if_then_constraint(self, clue):
        # Process "if x=a then y=b" or "if x=a then not y=b" type constraints
        match = re.match(r"if (\w+)=(\w+) then (not )?(\w+)=(\w+)", clue)
        if match:
            x, a, negate, y, b = match.groups()
            for subject in self.assignments:
                if self.assignments[subject].get(x) == a:
                    if negate and self.assignments[subject].get(y) == b:
                        return False
                    elif not negate and self.assignments[subject].get(y) != b:
                        return False
        return True

    def apply_inequality_constraint(self, clue):
        # Process numeric inequalities like "n(x=a) > n(y=b)"
        match = re.match(r"n\((\w+)=(\w+)\) (>|<) n\((\w+)=(\w+)\)", clue)
        if match:
            x, a, operator, y, b = match.groups()
            subjects_with_xa = [s for s in self.assignments if self.assignments[s].get(x) == a]
            subjects_with_yb = [s for s in self.assignments if self.assignments[s].get(y) == b]

            if subjects_with_xa and subjects_with_yb:
                subject_x = subjects_with_xa[0]
                subject_y = subjects_with_yb[0]
                value_x = int(self.assignments[subject_x]['years'])
                value_y = int(self.assignments[subject_y]['years'])
                if operator == '>' and not (value_x > value_y):
                    return False
                elif operator == '<' and not (value_x < value_y):
                    return False
        return True

    def apply_different_constraint(self, clue):
        # Process "{x=a, y=b, z=c} are all different" type constraints
        attributes = re.findall(r"(\w+)=(\w+)", clue)
        values = [self.assignments[subject].get(attribute) for attribute, value in attributes]
        return len(values) == len(set(values))

    def apply_one_of_constraint(self, clue):
        # Process "one of {x=a, y=b} corresponds to z=c other t=d" constraints
        match = re.findall(r"(\w+)=(\w+)", clue)
        if match:
            attr_a, val_a, attr_b, val_b = match[0][0], match[0][1], match[1][0], match[1][1]
            options = [(attr_a, val_a), (attr_b, val_b)]
            return any(self.assignments[subject].get(attr) == val for attr, val in options)
        return True

    def display_solution(self):
        # Check if the first attribute contains numeric values
        try:
            # Try to convert the first attribute's value for each assignment to int
            sorted_subjects = sorted(
                self.assignments.items(),
                key=lambda x: int(x[1][self.attributes[0]]) if x[1][self.attributes[0]].isdigit() else float('inf')
            )
        except ValueError:
            # If conversion fails, fallback to sorting by string (alphabetically)
            sorted_subjects = sorted(self.assignments.items(), key=lambda x: x[1][self.attributes[0]])

        # Display the sorted results
        print(" | ".join(self.attributes))
        print("-" * 40)
        for _, assignment in sorted_subjects:
            print(" | ".join(str(assignment[attr]) for attr in self.attributes))

# Usage example
puzzle = LogicPuzzleCSP('data-1.txt', 'clues-1.txt')
solution = puzzle.solve()
if solution:
    puzzle.display_solution()
else:
    print("No solution found.")
