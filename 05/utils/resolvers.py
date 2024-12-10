from collections import defaultdict
from pathlib import Path

SEPARATOR_RULES = "|"
SEPARATOR_PAGES = ","

def _read_and_process_file(filename: Path) -> list:
    """Reads a file and processes its contents to extract rules and updates.

    The file is expected to have two sections separated by a double newline:

    - The first section contains rules.
    - The second section contains updates.

    Args:
        filename (Path): Path to the file to be read.

    Returns:
        list: A list containing two elements:
              - A list of rules (str).
              - A list of updates (str).
    """
    with open(filename) as f:
        rules, updates = f.read().split("\n\n")

    return rules.split(), updates.split()

def _parse_rules(rules: list) -> dict:
    """Parses page ordering rules into dictionaries for easier validation
    of page order.

    Each rule is in the format `X|Y`, where `X` must be printed before `Y`
    if both are included in an update.

    Args:
        rules (list): A list of rules as strings.

    Returns:
        tuple: Two dictionaries:
            - `dict_rules_before` (defaultdict): Maps a page `Y`
                to a list of pages `X` that must appear before it.
            - `dict_rules_after` (defaultdict): Maps a page `X`
                to a list of pages `Y` that must appear after it.
    """
    dict_rules_before = defaultdict(list)
    dict_rules_after = defaultdict(list)

    for rule in rules:
        rule_number_before, rule_number_after = rule.split(SEPARATOR_RULES)

        dict_rules_before[rule_number_after].append(rule_number_before)
        dict_rules_after[rule_number_before].append(rule_number_after)

    return dict_rules_before, dict_rules_after

def _get_before_and_after(pages: list) -> list:
    """Returns a list of tuples where each tuple contains:

    - A list of elements before the current element.
    - A list of elements after the current element.

    Args:
        pages (list): The input list.

    Returns:
        list: A list of tuples (current, before, after) for each element.
    """
    result = []
    for i in range(len(pages)):
        current = pages[i]
        before = pages[:i]
        after = pages[i + 1:]
        result.append((current, before, after))
    return result

def _correct_pages_order(pages: list,
                         dict_rules_before: dict) -> list:
    """Ensures the pages are ordered correctly according to the given rules.

    Reorders the pages so that all rules in `dict_rules_before` are respected,
    where a rule `X|Y` specifies that page `X` must come before page `Y` if
    both pages are present.

    Args:
        pages (list): The list of page numbers to be ordered.
        dict_rules_before (dict): A dictionary where keys are page numbers
            (`Y`) and values are lists of page numbers (`X`) that must appear
            before the key.

    Returns:
        list: A corrected list of page numbers in the proper order,
            satisfying all rules.
    """
    pages_copy = pages[:]

    current_numbers_before = {
        number: [n for n in numbers_before if n in pages]
        for number, numbers_before in dict_rules_before.items()
        if number in pages and set(numbers_before).intersection(pages)
    }

    pages_corrected = []

    while pages_copy:
        for page_copy in pages_copy:
            if page_copy not in current_numbers_before:
                pages_corrected.append(page_copy)
                pages_copy.remove(page_copy)
                current_numbers_before = {
                    number: [n for n in numbers_before if n != page_copy]
                    for number, numbers_before in current_numbers_before.items()
                    if [n for n in numbers_before if n != page_copy]
                }

                break

    return pages_corrected

def first_exercise(filename: Path):
    rules, updates = _read_and_process_file(filename)
    dict_rules_before, dict_rules_after = _parse_rules(rules)

    middle_pages_to_sum = []
    for update in updates:
        pages = update.split(SEPARATOR_PAGES)
        correct_page = 0

        for current, before, after in _get_before_and_after(pages):
            applied_rules_before = all(
                page_before in dict_rules_before[current]
                for page_before in before
            )

            applied_rules_after = all(
                page_after in dict_rules_after[current]
                for page_after in after
            )

            if not applied_rules_before or not applied_rules_after:
                break
            else:
                correct_page += 1

        if correct_page == len(pages):
            middle_pages_to_sum.append(int(pages[len(pages) // 2]))

    return sum(middle_pages_to_sum)

def second_exercise(filename: Path):
    rules, updates = _read_and_process_file(filename)
    dict_rules_before, dict_rules_after = _parse_rules(rules)

    middle_pages_to_sum = []
    for update in updates:
        pages = update.split(SEPARATOR_PAGES)

        for current, before, after in _get_before_and_after(pages):
            applied_rules_before = all(
                page_before in dict_rules_before[current]
                for page_before in before
            )

            applied_rules_after = all(
                page_after in dict_rules_after[current]
                for page_after in after
            )

            if not applied_rules_before or not applied_rules_after:
                pages_corrected = _correct_pages_order(
                    pages, dict_rules_before
                )

                middle_pages_to_sum.append(
                    int(pages_corrected[len(pages_corrected) // 2])
                )
                break

    return sum(middle_pages_to_sum)
