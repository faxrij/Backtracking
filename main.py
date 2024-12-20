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
        puzzle.print_solution()
    else:
        print("No solution found.")

class LogicPuzzleCSP:
    attributes, values = None, None
    assignments = {}
    assigned_values = set()
    problem_number = None

    def __init__(self, data_file, clues_file, problem_number):
        self.attributes, self.values = self.parse_data(data_file)
        self.clues = self.parse_clues(clues_file)
        self.num_subjects = len(self.values[self.attributes[0]])
        self.assignments = {f'subject{i}': {} for i in range(self.num_subjects)}
        self.assigned_values = set()
        self.problem_number = problem_number

    def parse_data(self, data_file):
        attributes = []
        values = {}

        with open(data_file, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                attribute = parts[0]
                attributes.append(attribute)
                values[attribute] = parts[1:]

        return attributes, values

    def parse_clues(self, clues_file):
        clues = []

        with open(clues_file, 'r') as f:
            for line in f:
                clues.append(line.strip())

        return clues

    def set_variables(self):
        for i in range(self.num_subjects):
            for attribute in self.attributes:
                self.assignments[f'subject{i}'][attribute] = None

    def solve(self):
        self.set_variables()
        return self.backtrack(0)

    def backtrack(self, subject_index):
        if subject_index == self.num_subjects:
            if self.apply_constraints():
                return self.assignments
            return None

        current_subject = f'subject{subject_index}'
        for values in product(*[self.values[attr] for attr in self.attributes]):
            if any((attr, value) in self.assigned_values for attr, value in zip(self.attributes, values)):
                continue

            for attr, value in zip(self.attributes, values):
                self.assignments[current_subject][attr] = value
                self.assigned_values.add((attr, value))

            if self.apply_constraints():
                solution = self.backtrack(subject_index + 1)
                if solution:
                    return solution

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
        assigned_values = [(subject, self.assignments[subject].get(attribute)) for subject in self.assignments for attribute, value in attributes]
        return len(set([val for val in assigned_values if val is not None])) == len(attributes)

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
            options1, options2 = match.groups()
            options1 = options1.split(',')
            options2 = options2.split(',')
            for subject1, subject2 in product(self.assignments.items(), self.assignments.items()):
                if subject1 != subject2:
                    if all(subject1[1].get(attr) == value for attr, value in [option.split('=') for option in options1]) and \
                       all(subject2[1].get(attr) == value for attr, value in [option.split('=') for option in options2]):
                        return True
            return False

    def print_solution(self):
        if self.problem_number == 1:
            all_years = sorted(set(int(assignment.get('years', float('inf'))) for assignment in self.assignments.values()))
            print("years | owners | breeds | dogs")
            print("-" * 40)
            for year in all_years:
                for _, assignment in self.assignments.items():
                    if int(assignment.get('years', -1)) == year:
                        owners = assignment.get('owners', '')
                        breeds = assignment.get('breeds', '')
                        dogs = assignment.get('dogs', '')
                        print(f"{year} | {owners} | {breeds} | {dogs}")
        elif self.problem_number == 2:
            all_years = sorted(set(int(assignment.get('years', float('inf'))) for assignment in self.assignments.values()))
            print("years | players | teams | hometowns")
            print("-" * 40)
            for year in all_years:
                players, teams, hometowns = "", "", ""
                for _, assignment in self.assignments.items():
                    if int(assignment.get('years', -1)) == year:
                        players = assignment.get('players', '')
                        teams = assignment.get('teams', '')
                        hometowns = assignment.get('hometowns', '')
                print(f"{year} | {players} | {teams} | {hometowns}")

if __name__ == "__main__":
    main()