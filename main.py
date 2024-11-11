import re
from itertools import product

class LogicPuzzleCSP:
    attributes, values = None, None
    assignments = {f'subject{i}': {} for i in range(4)}
    assigned_values = set()

    def __init__(self, data_file, clues_file):
        self.attributes, self.values = self.parse_data_file(data_file)
        self.clues = self.parse_clues_file(clues_file)

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
        for i in range(4):
            for attribute in self.attributes:
                self.assignments[f'subject{i}'][attribute] = None

    def solve(self):
        self.initialize_variables()
        return self.backtrack(0)

    def backtrack(self, subject_index):
        if subject_index == len(self.assignments):
            if self.apply_constraints():
                return self.assignments
            return None

        current_subject = f'subject{subject_index}'
        for values in product(*[self.values[attr] for attr in self.attributes]):
            # Check for duplicate assignments across all subjects
            if any((attr, value) in self.assigned_values for attr, value in zip(self.attributes, values)):
                continue  # Skip this assignment and try the next one

            for attr, value in zip(self.attributes, values):
                self.assignments[current_subject][attr] = value
                self.assigned_values.add((attr, value))

            if self.apply_constraints():
                solution = self.backtrack(subject_index + 1)
                if solution:
                    return solution

            # Reset the subject's assignments and remove assigned values
            for attr, value in zip(self.attributes, values):
                self.assignments[current_subject][attr] = None
                self.assigned_values.remove((attr, value))
        return None

    # ... (rest of the code for applying constraints and displaying solution remains the same) ...

    def backtrack(self, subject_index):
        if subject_index == len(self.assignments):
            if self.apply_constraints():
                return self.assignments
            return None

        current_subject = f'subject{subject_index}'
        for values in product(*[self.values[attr] for attr in self.attributes]):
            # Check for duplicate assignments across all subjects
            if any((attr, value) in self.assigned_values for attr, value in zip(self.attributes, values)):
                continue  # Skip this assignment and try the next one

            for attr, value in zip(self.attributes, values):
                self.assignments[current_subject][attr] = value
                self.assigned_values.add((attr, value))

            if self.apply_constraints():
                solution = self.backtrack(subject_index + 1)
                if solution:
                    return solution

            # Reset the subject's assignments and remove assigned values
            for attr, value in zip(self.attributes, values):
                self.assignments[current_subject][attr] = None
                self.assigned_values.remove((attr, value))
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
            elif "either" in clue:
                if not self.apply_either_constraint(clue):
                    return False
        return True

    def apply_if_then_constraint(self, clue):
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
        match = re.match(r"years\((\w+)=(\w+)\) (>|<) years\((\w+)=(\w+)\)", clue)
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
        attributes = re.findall(r"(\w+)=(\w+)", clue)
        values = [self.assignments[subject].get(attribute) for attribute, value in attributes]
        return len(values) == len(set(values))

    def apply_either_constraint(self, clue):
        match = re.match(r"if dogs=(\w+) then either (.+)", clue)
        if match:
            dog, options = match.groups()
            options = options.split(" or ")
            for subject in self.assignments:
                if self.assignments[subject].get('dogs') == dog:
                    for option in options:
                        attr, value = option.split('=')
                        if self.assignments[subject].get(attr) == value:
                            return True
                    return False
        return True

    def display_solution(self):
        all_years = sorted(set(int(assignment.get('years', float('inf'))) for assignment in self.assignments.values()))
        print("years | owners | breeds | dogs")
        print("-" * 40)
        for year in all_years:
            for subject, assignment in self.assignments.items():
                if int(assignment.get('years', -1)) == year:
                    owners = assignment.get('owners', '')
                    breeds = assignment.get('breeds', '')
                    dogs = assignment.get('dogs', '')
                    print(f"{year} | {owners} | {breeds} | {dogs}")

# Usage example
puzzle = LogicPuzzleCSP('data-1.txt', 'clues-1.txt')
solution = puzzle.solve()
if solution:
    puzzle.display_solution()
else:
    print("No solution found.")