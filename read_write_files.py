import argparse
import time
from wikidata_search_each import FindWikiPage
# from find_wiki_page import FindWikiPage
import re
import multiprocessing
import pprint

class ReadWrite():
    return_values = []

    def open_file(self, file_in):
        with open(file_in, 'r') as file_in:
            lines = []
            for line in file_in:
                values = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)
                values[-1] = values[-1].strip()
                for value_nb in range(len(values)):
                    values[value_nb] = values[value_nb].replace('"', '')
                lines.append(values)

        return lines

    def write_file(self, file_out, data):
        with open(file_out, 'w+') as the_file:
            pass
        wiki = 'https://www.wikidata.org/wiki/'
        with open(file_out, 'a') as the_file:
            for d in data:
                dk = []
                for each_d in range(len(d)):
                    if d[each_d] != '':
                        dk.append(wiki + d[each_d])
                    else:
                        dk.append(d[each_d])
                the_file.write(f'{dk[0]},{dk[1]},{dk[2]},{dk[3]},{dk[4]}\n')

    def for_multiprocessing(self, dict_to_find):
        find_wiki = FindWikiPage()
        print(f"\n ----- Row number {dict_to_find['number']} is searching")
        found = {'number': dict_to_find['number'],
                            'list': find_wiki.start(dict_to_find['list'])}
        # print(f"self.return_values::: {self.return_values}")
        # self.return_values.append(found)
        return found


    def main(self, file_in, file_out, quantity):
        """Main Function"""
        # options = get_arg()

        start = time.time()

        file = self.open_file(file_in)[0:quantity]
        print(file)
        output_list = []
        number = 0
        find_wiki = FindWikiPage()

        for data in file:
            number += 1
            print(f"\n ----- Row number {number} is searching")

            id_found = find_wiki.start(data)
            output_list.append(id_found)

        self.write_file(file_out, output_list)
        end = time.time() - start
        m, s = divmod(end, 60)
        print("Time spent: {} min {} sec.".format(int(m), s))

    def main_multiproc(self, file_in, file_out, quantity):
        """Main Function"""
        # options = get_arg()

        start = time.time()

        file = self.open_file(file_in)[0:quantity]
        print(file)
        number = -1

        new_data_list = []
        for data in file:
            number += 1

            new_data_list.append({'number': number,
                                  'list': data})

        pool = multiprocessing.Pool()
        result = pool.map(self.for_multiprocessing, new_data_list)
        pool.close()
        pprint.pprint(result)
        result1 = []
        for res in result:
            result1.append(res['list'])

        self.write_file(file_out, result1)
        end = time.time() - start
        m, s = divmod(end, 60)
        print("Time spent: {} min {} sec.".format(int(m), s))

def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", type=str, required=True,
                        help="File, that has to be read")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="File, where information has to be written")
    return parser.parse_args()


if __name__ == "__main__":
    # main("Data\\Input\\input_data1.csv",
    #      "Data\\new.csv", 50)
    ReadWrite().main_multiproc("Data\\Input\\input_data1.csv",
         "Data\\new.csv", 500)

