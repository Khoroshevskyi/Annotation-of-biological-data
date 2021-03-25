import argparse
import time
from find_wiki_page import FindWikiPage
import re


def open_file(file_in):
    with open(file_in, 'r') as file_in:
        lines = []
        for line in file_in:
            values = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)
            values[-1] = values[-1].strip()
            for value_nb in range(len(values)):
                values[value_nb] = values[value_nb].replace('"', '')
            lines.append(values)

    return lines


def write_file(file_out, data):
    wiki = 'https://www.wikidata.org/wiki/'
    with open(file_out, 'a') as the_file:
        for d in data:
            the_file.write(f'{wiki+d[0]},{wiki+d[1]},{wiki+d[2]},{wiki+d[3]},{wiki+d[4]}\n')


def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", type=str, required=True,
                        help="File, that has to be read")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="File, where information has to be write")
    return parser.parse_args()


def main(file_in, file_out):
    """Main Function"""
    # options = get_arg()
    
    start = time.time()
    find_wiki = FindWikiPage()
    file = open_file(file_in)[0:200]
    output_list = []
    number = 0
    for data in file:
        number += 1
        print(f"row number {number} is searchin")
        id_found = find_wiki.start(data)
        output_list.append(id_found)
    write_file(file_out,output_list)
    end = time.time() - start

    m, s = divmod(end, 60)
    print("Time spent: {} min {} sec.".format(int(m), s))


if __name__ == "__main__":
    main("C:\\Users\\pawlo\\Downloads\\input_data\\input_data1.csv" ,
         "C:\\Users\\pawlo\\Downloads\\input_data\\new.csv")
