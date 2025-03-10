import json
import re


def load_entries():
    with open('library_collection.json', 'r') as incoming:
        return json.load(incoming)


def discrepancy_list(entries: list[dict]):
    broken_entries = []

    for entry in entries:
        if ratings_have_discrepancies(entry["user_rating"]):
            broken_entries.append(entry)
        elif formats_have_discrepancies(entry["format"]):
            broken_entries.append(entry)
        elif read_dates_have_discrepancies(entry["date_read"]):
            broken_entries.append(entry)
        elif tags_have_discrepancies(entry["tags"]):
            broken_entries.append(entry)
        elif read_status_has_discrepancies(entry["status"]):
            broken_entries.append(entry)
        elif read_counts_have_discrepancies(entry["read_count"]):
            broken_entries.append(entry)
        elif owned_counts_have_discrepancies(entry["owned_count"]):
            broken_entries.append(entry)

    return broken_entries


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
        # Both items exist and one contains the other
        if entry_formats[0].lower() in entry_formats[1].lower():
            return False
        elif entry_formats[1].lower() in entry_formats[0].lower():
            return False
        # Both items exist, but aren't the same
        else:
            return True

    # Only one item exists - there is a discrepancy
    elif entry_formats[0] or entry_formats[1]:
        return True
    # Neither item exists
    else:
        return False


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
    """
    Returns True if the tags do not match. Otherwise, returns False.
    :param entry_tags: A list of two items. They must be str or None.
    :return:
    """
    first_tags = filtered_tag_set(entry_tags[0])
    second_tags = filtered_tag_set(entry_tags[1])

    if first_tags == second_tags:
        return False
    else:
        return True


def read_status_has_discrepancies(entry_status):
    """
    Returns True if the statuses do not match. Otherwise, returns False.
    :param entry_status: A list of two items. They must be str or None.
    :return:
    """
    # Items match - No discrepancy
    if entry_status[0] == entry_status[1]:
        return False
    # Items do not match, but mean the same thing. No discrepancy.
    elif {entry_status[0], entry_status[1]} <= {"dropped", "did-not-finish"}:
        return False
    # Items are not the same. There is a discrepancy.
    else:
        return True


def read_counts_have_discrepancies(entry_read_counts):
    """
    Returns True if the read counts do not match. Otherwise, returns False.
    :param entry_read_counts:
    :return:
    """
    # Read counts match - no discrepancy
    if entry_read_counts[0] == entry_read_counts[1]:
        return False
    # One read count is 0 and the other is None - identical meanings, and no discrepancy
    elif not entry_read_counts[0] and not entry_read_counts[1]:
        return False
    # At least one read count exists, but they aren't the same. There is a discrepancy.
    else:
        return True


def owned_counts_have_discrepancies(entry_owned_counts):
    """
    Returns True if the read counts do not match. Otherwise, returns False.
    :param entry_owned_counts: A list of two items. The first is int or None. The second is str or None.
    :return:
    """
    if bool(entry_owned_counts[0]) != yn_bool(entry_owned_counts[1]):
        return True
    else:
        return False


def truthiness_matches(item_a, item_b):
    if bool(item_a) == bool(item_b):
        return True
    else:
        return False


def yn_bool(yn: str) -> bool:
    if yn == "Yes":
        return True
    else:
        return False


def filtered_tag_set(str_tags: str) -> set:
    """
    Takes a comma-separated string of tags and returns a set of all tags except 'to-read'.
    If no tags are present, returns empty set.
    :param str_tags:
    :return:
    """
    list_tags = []
    if str_tags:
        list_tags = re.findall(r'\w+\-?\w+', str_tags)
        if "to-read" in list_tags:
            list_tags.remove("to-read")
    return set(list_tags)


def find_entry(entries: dict):
    print(entries[0])
