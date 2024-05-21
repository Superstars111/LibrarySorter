from collection import collect_entries, dump_entries
from analysis import load_entries, find_entry, discrepancy_list
from pprint import pprint


def list_items(listed_entries):
    for idx, entry in enumerate(listed_entries):
        print(f"You are on entry {idx+1} of {len(listed_entries)}")
        pprint(entry, sort_dicts=False)
        input("Press enter to continue...")
        continue


def determine_user_action():
    action = None
    scope = None
    while not action:
        action = input("What action would you like? Collect, analyze?: ").lower()
        if action == "collect":
            while not scope:
                scope = input("Would you like to gather [Goodreads], [Storygraph], or [All] data?: ").lower()
                if scope == "goodreads":
                    print("Not implemented")
                    scope = None
                elif scope == "storygraph":
                    print("Not implemented")
                    scope = None
                elif scope == "all":
                    entries, broken_entries = collect_entries()
                    dump_entries(entries, broken_entries)
                else:
                    print("Invalid")
                    scope = None

        elif action == "analyze":
            entries = load_entries()
            print(f"There are {len(entries[0])} entries with matches")
            print(f"There are {len(entries[1])} entries with no match")
            mismatched_entries = discrepancy_list(entries[0])
            print(f"There are {len(mismatched_entries)} matched entries with discrepancies")

            while not scope:
                scope = input("Which list would you like to view? Mismatched, or single?: ").lower()
                if scope == "mismatched":
                    list_items(mismatched_entries)

                elif scope == "single":
                    list_items(entries[1])

                else:
                    print("Invalid")
                    scope = None

        else:
            print(f"Invalid: {action}, {type(action)}")
            action = None


if __name__ == '__main__':

    determine_user_action()
