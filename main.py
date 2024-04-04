from collection import collect_entries, dump_entries
from analysis import load_entries, find_entry, find_discrepancies


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

        elif action == "analyze":
            entries = load_entries()
            find_discrepancies(entries[0])
            # find_entry(entries)

        else:
            print(f"Invalid: {action}, {type(action)}")
            action = None


if __name__ == '__main__':

    determine_user_action()
