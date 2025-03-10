import pandas as pd
import json
import re
from copy import deepcopy


class Book:
    def __init__(self):
        self.included = [None, None, None]
        self.title = [None, None]
        self.author = [None, None]
        self.isbn = [None, None]
        self.user_rating = [None, None]
        self.format = [None, None]
        self.date_read = [None, None]
        self.tags = [None, None]
        self.status = [None, None]
        self.read_count = [None, None]
        self.owned_count = [None, None]


def collect_entries():
    """
    Entry point for collection of data. Returns lists of dictionaries containing selected data from csv files
    generated by Goodreads and Storygraph. File locations are currently hardcoded.
    :return:
    """
    complete_entries = []
    broken_entries = []

    # Goodreads - Initial entries population
    entries, faulty_entries = populate_entries_list()
    broken_entries.extend(faulty_entries)

    # Storygraph - Editing and appending to entries
    entries, faulty_entries = append_to_entries_list(entries)
    broken_entries.extend(faulty_entries)

    print("Now merging: entries")
    # Entries list is sorted into "solid" and "half" entries. All have ISBNs.
    # Books from "broken" which are no longer needed are put into "merged." None have ISBNs.
    solid_entries, half_entries, merged_entries = solidify(entries, broken_entries)
    complete_entries.extend(solid_entries)
    broken_entries = filter_duplicates(broken_entries, merged_entries)
    half_entries.extend(broken_entries)

    print("Now merging: half_entries")
    solid_entries, half_entries, merged_entries = solidify(half_entries)
    complete_entries.extend(solid_entries)

    return complete_entries, half_entries


def assign_goodreads_data_to_book(csv_data: tuple, entry: Book = None) -> Book:

    if entry is None:
        entry = Book()

    entry.included[0] = "Goodreads"
    entry.title[0] = csv_data[2]
    entry.author[0] = csv_data[3]
    entry.isbn[0] = translate_goodreads_isbn(csv_data[7])
    entry.user_rating[0] = csv_data[8]
    entry.format[0] = nan_filter(csv_data[11])
    entry.date_read[0] = nan_filter(csv_data[15])
    entry.tags[0] = nan_filter(csv_data[17])
    entry.status[0] = csv_data[19]
    entry.read_count[0] = csv_data[23]
    entry.owned_count[0] = csv_data[24]

    return entry


def assign_storygraph_data_to_book(csv_data: tuple, entry: Book = None) -> Book:

    if entry is None:
        entry = Book()

    entry.included[1] = "Storygraph"
    entry.title[1] = csv_data[1]
    entry.author[1] = nan_filter(csv_data[2])
    # Default is float, so I can't just put in the value directly. But I can't int(None).
    if not is_nan(csv_data[4]):
        entry.isbn[1] = int(csv_data[4])
    entry.user_rating[1] = nan_filter(csv_data[18])
    entry.format[1] = nan_filter(csv_data[5])
    entry.date_read[1] = nan_filter(csv_data[9])
    entry.tags[1] = nan_filter(csv_data[22])
    entry.status[1] = nan_filter(csv_data[6])
    entry.read_count[1] = nan_filter(csv_data[10])
    entry.owned_count[1] = csv_data[23]

    return entry


def collect_csv_data(file_path: str):
    with open(file_path, 'r') as csvfile:
        csv_data = pd.read_csv(csvfile)
        return csv_data


def generate_keys(source: str) -> dict:
    """
    :param source: Goodreads or Storygraph
    :return: Dict containing strings, functions, and integers for working with csv data from Goodreads or Storygraph.
    """
    # TODO: Make more efficient
    source = source.lower()
    source_keys = {
        "csv_location": f"{source}_library_export"
    }

    if source == "goodreads":
        source_keys["primary_idx"] = 0
        source_keys["secondary_idx"] = 1
        source_keys["isbn_column"] = 7
        source_keys["entry_generator"] = assign_goodreads_data_to_book

    elif source == "storygraph":
        source_keys["primary_idx"] = 1
        source_keys["secondary_idx"] = 0
        source_keys["isbn_column"] = 4
        source_keys["entry_generator"] = assign_storygraph_data_to_book

    else:
        raise ValueError("Value must equal 'Goodreads' or 'Storygraph'")

    return source_keys


def populate_entries_list(population_type: str = "Goodreads"):
    """
    :param population_type: Goodreads or Storygraph
    :return: Two lists of entries, containing entries with and without ISBNs respectively
    """
    entries = []
    faulty_entries = []

    population_keys = generate_keys(population_type)
    raw_data = collect_csv_data(f"/home/jared/Documents/spreadsheets/{population_keys['csv_location']}.csv")

    for row in raw_data.itertuples():
        new_entry = population_keys["entry_generator"](row)
        if new_entry.isbn[population_keys["primary_idx"]]:
            entries.append(new_entry)
        else:
            faulty_entries.append(new_entry)

    return entries, faulty_entries


def append_to_entries_list(entries: list[Book], population_type: str = "Storygraph"):
    # TODO: Condense
    faulty_entries = []

    population_keys = generate_keys(population_type)
    raw_data = collect_csv_data(f"/home/jared/Documents/spreadsheets/{population_keys['csv_location']}.csv")
    generator = population_keys["entry_generator"]
    isbn_col = population_keys["isbn_column"]

    for row in raw_data.itertuples():
        # If the current entry has an ISBN, put it in the main list
        if not is_nan(row[isbn_col]):
            for idx, entry in enumerate(entries):
                # If finding an existing entry with a matching ISBN, add data to that entry
                if row[isbn_col] == entry.isbn[population_keys["secondary_idx"]]:
                    generator(row, entry)
                    print(f"Matching entry for {entry.title}")
                    break
            # If reaching the end of the list with no matches, add the new entry at the end
            else:
                new_entry = generator(row)
                entries.append(new_entry)
                print(f"No matches: {new_entry.title}")

        # If the current entry has no ISBN, put it in the faulty list
        else:
            new_entry = generator(row)
            faulty_entries.append(new_entry)
            print(f"No ISBN: {new_entry.title}")

    return entries, faulty_entries


def match_entries(main_entry: Book, merging_entry: Book, needed_idx: int) -> str:
    """
    Presents the user with the option to merge or skip a set of two entries.
    Returns a string indicating the action taken.
    :param main_entry:
    :param merging_entry:
    :param needed_idx:
    :return: "merged" or "skipped"
    """
    print("Broken entry:", merging_entry.__dict__,
          "\n", "Full entry:", main_entry.__dict__, "\n")
    action = None
    while action is None:
        action = input("Please select Merge or Skip: ").lower()
        if action == "merge":
            merge(main_entry, merging_entry, needed_idx)
            return "merged"
        elif action not in ("skip", "merge"):
            print("Invalid, please try again.")
            action = None

    return "skipped"


def merge(main_entry: Book, merging_entry: Book, needed_idx: int):
    for key, value in main_entry.__dict__.items():
        value[needed_idx] = merging_entry.__dict__[key][needed_idx]


def solidify(main_entries: list[Book], merging_entries: list[Book] = None):
    """
    Takes a list of Books where some entries should have been merged but were not, and merges those entries.
    main_entries is sorted into "solid" and "single" entries. Data from "merging_entries" is either added to a "solid"
    entry and appended to "merged_entries," or is left untouched.
    :param main_entries:
    :param merging_entries:
    :return:
    """
    entries_are_copied = not bool(merging_entries)
    if entries_are_copied:
        merging_entries = deepcopy(main_entries)

    solid_entries = []
    single_entries = []
    merged_entries = []

    for entry in main_entries:
        needed_idx, owned_idx, = included_indices(entry)
        if needed_idx == 1 and owned_idx == 1:  # Check if entry is already solid
            check_isbn(entry, 1)  # TODO: Remove when bug is fixed
            solid_entries.append(entry)
            continue
        elif entry.included[2]:
            continue

        for merge_idx, merger in enumerate(merging_entries):
            if merger.included[owned_idx]:
                continue
            elif titles_are_inclusive(entry.title[owned_idx], merger.title[needed_idx]):
                status = match_entries(entry, merger, needed_idx)
                if status == "merged":
                    check_isbn(entry, 2)  # TODO: Remove when bug is fixed
                    solid_entries.append(entry)
                    merged_entries.append(merger)
                    if entries_are_copied:
                        main_entries[merge_idx].included[2] = "Merged"
                    break
        else:
            check_isbn(entry, 3)  # TODO: Remove when bug is fixed
            single_entries.append(entry)

    return solid_entries, single_entries, merged_entries


def filter_duplicates(entries: list[Book], used_entries: list[Book]):
    # TODO: Check logic
    unused_entries = []
    for entry in entries:
        if entry not in used_entries:
            unused_entries.append(entry)

    return unused_entries


def dump_entries(*data_lists):
    with open('library_collection.json', 'w') as outfile:
        json.dump(data_lists, outfile, indent=4, default=lambda o: o.__dict__)


def translate_goodreads_isbn(isbn: str):
    """
    :param isbn: A string containing an isbn.
    :return: If a match is found, returns an int of the isbn. Otherwise, returns None instead.
    """

    isbn_match = re.search(r'\d+', isbn)
    if isbn_match:
        isbn_match = int(isbn_match.group())
    return isbn_match


def is_nan(value) -> bool:
    """
    Returns True if the given value is NaN; otherwise, returns False
    """
    if str(value) == "nan":
        return True
    else:
        return False


def nan_filter(value):
    """
    Returns None if the given value is NaN; otherwise, returns given value
    """
    if is_nan(value):
        return None
    else:
        return value


def included_data(entry: Book):
    goodreads_included = False
    storygraph_included = False

    if entry.included[0]:
        goodreads_included = True
    if entry.included[1]:
        storygraph_included = True

    return goodreads_included, storygraph_included


def included_indices(entry: Book):
    """
    Returns 1 for included data, and 0 for needed data.
    The first will be an inverted index, while the second will be a true index.
    :param entry:
    :return:
    """
    goodreads_bool, storygraph_bool = included_data(entry)
    goodreads_idx = int(goodreads_bool)
    storygraph_idx = int(storygraph_bool)
    return goodreads_idx, storygraph_idx


def titles_are_inclusive(first_title: any, second_title: any) -> bool:
    """
    Checks it two titles match or if one includes the other.
    If anything other than strings are submitted, returns False by default.
    :param first_title: A string containing the first title
    :param second_title: A string containing the second title
    :return: False by default. True if one title is in the other.
    """
    potential_match_found = False
    try:
        if first_title in second_title:
            potential_match_found = True
        elif second_title in first_title:
            potential_match_found = True
    except TypeError:
        print(f"There was an error. You submitted {first_title} and {second_title}.")
    finally:
        return potential_match_found


def check_isbn(book: Book, location: int):
    """
    Janky function used for bugtesting
    :param book:
    :param location:
    :return:
    """
    if book.isbn[0] == 9781250811066:
        print(f"Appending to list at location {location}: {book.title}")
