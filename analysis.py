import json


def load_entries():
    with open('library_collection.json', 'r') as incoming:
        return json.load(incoming)


def find_discrepancies(entries):
    entries_with_discrepancies = []

    for entry in entries:
        if ratings_have_discrepancies(entry):
            entries_with_discrepancies.append(entry)
        elif formats_have_discrepancies(entry):
            entries_with_discrepancies.append(entry)
        elif read_dates_have_discrepancies(entry):
            entries_with_discrepancies.append(entry)
        elif tags_have_discrepancies(entry):
            entries_with_discrepancies.append(entry)
        elif read_status_has_discrepancies(entry):
            entries_with_discrepancies.append(entry)
        elif read_counts_have_discrepancies(entry):
            entries_with_discrepancies.append(entry)
        elif owned_counts_have_discrepancies(entry):
            entries_with_discrepancies.append(entry)

    return entries_with_discrepancies


def ratings_have_discrepancies(entry_ratings: list) -> bool:
    """
    Returns True if the ratings do not match. Otherwise, returns False.
    :param entry_ratings: A list of two items. The first must be an int or None.
    :return:
    """
    # If both are not 0/None
    if entry_ratings[0] and entry_ratings[1]:
        # If they match, no discrepancy
        if float(entry_ratings[0]) == entry_ratings[1]:
            return False
        # If they don't match, discrepancy
        else:
            return True
    # If at least one has no rating
    else:
        # If only one is blank, discrepancy
        if entry_ratings[0] or entry_ratings[1]:
            return True
        # If both are blank, no discrepancy
        else:
            return False


def formats_have_discrepancies(entry_formats):
    """
    Returns True if the formats do not match. Otherwise, returns False.
    :param entry_formats: A list of two items. They must be str or None.
    :return:
    """

    if entry_formats[0] and entry_formats[1]:
        if entry_formats[0].lower() in entry_formats[1].lower():
            return False
        elif entry_formats[1].lower() in entry_formats[0].lower():
            return False
        else:
            return True


def read_dates_have_discrepancies(entry_read_dates):
    """
    Returns True if the read dates do not match. Otherwise, returns False.
    Dates from both Goodreads and Storygraph are logged in YYYY/MM/DD format.
    :param entry_read_dates: A list of two items. They must be str or None.
    :return:
    """

    if entry_read_dates[0] == entry_read_dates[1]:
        return False
    else:
        return True


def tags_have_discrepancies(entry_tags):
    pass


def read_status_has_discrepancies(entry_status):
    pass


def read_counts_have_discrepancies(entry_read_counts):
    pass


def owned_counts_have_discrepancies(entry_owned_counts):
    pass


def truthiness_matches(item_a, item_b):
    if bool(item_a) == bool(item_b):
        return True
    else:
        return False


def find_entry(entries: dict):
    print(entries[0])
