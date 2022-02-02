import argparse
import os
import hashlib


def get_paths():

    parser = argparse.ArgumentParser(description="This program prints a bunch of files from a specified directory")

    parser.add_argument("path", default=False, nargs='?')

    print(parser.parse_args())
    args = parser.parse_args()
    path_string = args.path

    if not path_string:
        print("Directory is not specified")

    else:
        file_list = []

        for root, dirs, files in os.walk(path_string):
            for name in files:
                file_list.append(os.path.join(root, name))

        return file_list


def get_sorting_option():

    print("Size sorting options:\n1. Descending\n2. Ascending\n")
    while True:
        option = input("Enter a sorting option:")
        if option == '1':
            return True
        elif option == '2':
            return False
        else:
            print("Wrong option\n")


def get_sorted_dict(paths, ext, sort_option):

    output_dict = {}
    paths.sort(key=os.path.getsize, reverse=sort_option)

    if ext == '': # keep all files if no extension provided
        paths = {x: os.path.getsize(x) for x in paths}
    else:
        ext = "." + ext
        paths = {x: os.path.getsize(x) for x in paths if os.path.splitext(x)[1] == ext}

    # iterate through dict, making new dict where each key is a file size, and value is a list of paths
    for path, size in paths.items():

        if size not in output_dict.keys():
            output_dict[size] = [path]
        else:
            output_dict[size].append(path)

    return output_dict


def get_hash_of_file(path):

    with open(path, "rb") as file_1:
        return hashlib.md5(file_1.read()).hexdigest()


def get_hashes(files):

    hash_dict = {}
    for size, paths in files.items():
        hash_dict[size] = {}

        if len(paths) >= 2:
            for path in paths:
                h = get_hash_of_file(path)
                if h not in hash_dict[size].keys():
                    hash_dict[size][h] = [path]
                else:
                    hash_dict[size][h].append(path)

    return hash_dict


def remove_singletons(input_dict):

    output_dict = {}

    for size, hash_dict in input_dict.items():
        output_dict[size] = {}
        for hash_key, paths in hash_dict.items():
            if len(paths) >= 2:
                output_dict[size][hash_key] = paths
        if output_dict[size] == {}:
            output_dict.pop(size)

    return output_dict


def print_hash_dups_and_get_list(input_dict): # outputs list of tuples (path to file, size) for possible deletion later

    output_list = []
    i = 1
    for size, hash_dict in input_dict.items():
        print(f"\n{size} bytes")

        for hash_key, files in hash_dict.items():
            print(f"Hash: {hash_key}")

            for filename in files:
                output_list.append((filename, size)) # add filename to output list
                filename = f"{i}. {filename}" # add number to front of file path
                print(filename)
                i += 1

    return output_list


def main():

    user_choice = None
    possible_dups = {}

    all_files = get_paths()
    what_format = input("Enter file format:")
    sorting = get_sorting_option()  # 1 = Ascending, 2 = Descending

    all_files = get_sorted_dict(all_files, what_format, sorting)

    for b, f_lst in all_files.items():
        print(f"{b} bytes")
        # any dict value with more than 1 file path, add to separate dict to be checked for dups later
        if len(f_lst) > 1:
            possible_dups[b] = f_lst
        for file in f_lst:
            print(file)
        print()

    # duplicate check section
    while user_choice not in ["yes", "no"]:
        user_choice = input("Check for duplicates?")
        if user_choice == "yes":
            # get hash of possible duplicate files
            possible_dups = remove_singletons(get_hashes(possible_dups))
            deletion_list = print_hash_dups_and_get_list(possible_dups)
            user_choice = None

            # delete check section
            while user_choice not in ["yes", "no"]:
                user_choice = input("\nDelete files?")
                if user_choice == "yes":

                    while True:
                        try:
                            delete_choice = [int(x) for x in input("\nEnter file numbers to delete:").split()]
                        except ValueError:
                            print("\nWrong format")
                            continue

                        if len(delete_choice) == 0 or max(delete_choice) > len(deletion_list) or min(delete_choice) < 1:
                            print("\nWrong format")
                            continue

                        deleted_bytes = 0

                        for d in delete_choice:
                            os.remove(deletion_list[d-1][0])
                            deleted_bytes += deletion_list[d-1][1]

                        print(f"\nTotal freed up space: {deleted_bytes}")
                        break


if __name__ == "__main__":
    main()






