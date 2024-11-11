import re
from itertools import product

def main():
    print("The problems available in this directory: 1 2 3")
    problem_choice = int(input("Choose a problem: "))

    data_file = f"data-{problem_choice}.txt"
    clues_file = f"clues-{problem_choice}.txt"

    puzzle = LogicPuzzleCSP(data_file, clues_file, problem_choice)
    solution = puzzle.solve()

    if solution:
        puzzle.display_solution()
    else:
        print("No solution found.")

class LogicPuzzleCSP:
    attributes, values = None, None
    assignments = {}
    assigned_values = set()
    problem_number = None

    def __init__(self, data_file, clues_file, problem_number):
        self.attributes, self.values = self.parse_data_file(data_file)
        self.clues = self.parse_clues_file(clues_file, problem_number)
        self.num_subjects = len(self.values[self.attributes[0]])
        self.assignments = {f'subject{i}': {} for i in range(self.num_subjects)}
        self.assigned_values = set()
        self.problem_number = problem_number

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

    def parse_clues_file(self, clues_file, problem_number):
        clues = []

        with open(clues_file, 'r') as f:
            for line in f:
                clues.append(line.strip())

        return clues

    def initialize_variables(self):
        for i in range(self.num_subjects):
            for attribute in self.attributes:
                self.assignments[f'subject{i}'][attribute] = None

    def solve(self):
        self.initialize_variables()
        return self.backtrack(0)

    def backtrack(self, subject_index):
        if subject_index == self.num_subjects:
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
            elif "=" in clue:
                if not self.apply_equality_constraint(clue):
                    return False
            elif "one of" in clue:
                if not self.apply_one_of_constraint(clue):
                    return False
            # Add specific constraints for problem 1 and 2 here
            elif self.problem_number == 1:
                # Check for problem 1 specific constraints, e.g., age-related constraints
                pass
            elif self.problem_number == 2:
                # Check for problem 2 specific constraints
                pass
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
        match = re.match(r"n\((.+)\) (>|<) n\((.+)\)", clue)
        if match:
            attr1, value1 = match.group(1).split('=')
            attr2, value2 = match.group(2).split('=')
            for subject1, subject2 in product(self.assignments.items(), self.assignments.items()):
                if subject1 != subject2:
                    if subject1[1].get(attr1) == value1 and subject2[1].get(attr2) == value2:
                        if operator == '>' and not (int(subject1[1]['years']) > int(subject2[1]['years'])):
                            return False
                        elif operator == '<' and not (int(subject1[1]['years']) < int(subject2[1]['years'])):
                            return False
        return True

    def apply_different_constraint(self, clue):
        attributes = re.findall(r"(\w+)=(\w+)", clue)
        values = [self.assignments[subject].get(attribute) for attribute, value in attributes]
        return len(values) == len(set(values))

    def apply_either_constraint(self, clue):
        match = re.match(r"if (\w+)=(\w+) then either (.+) or (.+)", clue)
        if match:
            x, a, option1, option2 = match.groups()
            for subject in self.assignments:
                if self.assignments[subject].get(x) == a:
                    if not (self.assignments[subject].get(option1.split('=')[0]) == option1.split('=')[1] or
                            self.assignments[subject].get(option2.split('=')[0]) == option2.split('=')[1]):
                        return False
        return True

    def apply_equality_constraint(self, clue):
        match = re.match(r"n\((.+)\) = n\((.+)\)", clue)
        if match:
            attr1, value1 = match.group(1).split('=')
            attr2, value2 = match.group(2).split('=')
            for subject1, subject2 in product(self.assignments.items(), self.assignments.items()):
                if subject1 != subject2:
                    if subject1[1].get(attr1) == value1 and subject2[1].get(attr2) == value2:
                        if int(subject1[1]['years']) != int(subject2[1]['years']):
                            return False
        return True

    def apply_one_of_constraint(self, clue):
        match = re.match(r"one of {(.+)} corresponds to (.+) other (.+)", clue)
        if match:
            options1, cond1, options2, cond2 = match.groups()
            options1 = options1.split(',')
            options2 = options2.split(',')
            for subject1, subject2 in product(self.assignments.items(), self.assignments.items()):
                if subject1 != subject2:
                    if all(subject1[1].get(attr) == value for attr, value in [option.split('=') for option in options1]) and \
                       all(subject2[1].get(attr) == value for attr, value in [option.split('=') for option in options2]):
                        return True
            return False

    def display_solution(self):
        all_years = sorted(set(int(assignment.get('years', float('inf'))) for assignment in self.assignments.values()))
        print("years | players | teams | hometowns")
        print("-" * 40)

        # Loop through years
        for year in all_years:
            players, teams, hometowns = "", "", ""

            # Loop through subjects and find matching year
            for subject, assignment in self.assignments.items():
                if int(assignment.get('years', -1)) == year:
                    players = assignment.get('players', '')
                    teams = assignment.get('teams', '')
                    hometowns = assignment.get('hometowns', '')

            print(f"{year} | {players} | {teams} | {hometowns}")

if __name__ == "__main__":
    main()