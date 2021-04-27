import time
from wikidata_search_each import FindWikiPage
import re
import multiprocessing
import pprint
import json


class ReadWrite(object):

    def __init__(self, data_instances=None, api_search_quantity=20):
        self.return_values = []
        self.data_instances = data_instances
        self.api_search_quantity = api_search_quantity

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

    def get_instances_of_raw_data(self, file_in, quantity, with_instance=True):
        raw_data = self.open_file(file_in)[0:quantity]

        new_list = []
        for rawd in raw_data:
            find_wiki = FindWikiPage(api_search_quantity=self.api_search_quantity)
            find_wiki.search(rawd)
            # print("Searching: ", rawd)
            ids_with_instances = find_wiki.get_list_of_possible_answers(with_instances=with_instance)
            # print("Output: ")
            # pprint.pprint(ids_with_instances)
            for found in ids_with_instances:
                new_list.append(found["instances"])

        value_counter = self.count_most_popular(new_list)
        self.print_in_percent(value_counter)

    def count_most_popular(self, list_to_count):
        value_counter = [{} for k in range(len(list_to_count[0]))]
        for one_found in list_to_count:
            for col_number in range(len(one_found)):
                try:
                    value_counter[col_number][one_found[col_number]] += 1
                except KeyError:
                    value_counter[col_number][one_found[col_number]] = 1

        return value_counter

    def print_in_percent(self, value_counter):
        numb = 0
        for val in value_counter:
            numb += 1
            print(f"### numb: {numb}")
            s = sum(val.values())
            for k, v in val.items():
                pct = v * 100.0 / s
                print(f"# {k} --> {round(pct, 2)}%")

    def main_normal(self, file_in, file_out, quantity):
        """Main Function"""

        start = time.time()

        file = self.open_file(file_in)[0:quantity]
        print(file)
        output_list = []
        number = 0
        find_wiki = FindWikiPage(self.data_instances, api_search_quantity=self.api_search_quantity)

        for data in file:
            number += 1
            print(f"\n ----- Row number {number} is searching")
            id_found = find_wiki.search_and_get(data)
            output_list.append(id_found)

        self.write_file(file_out, output_list)
        end = time.time() - start
        m, s = divmod(end, 60)
        print("Time spent: {} min {} sec.".format(int(m), s))

    def for_multiprocessing(self, dict_to_find):
        find_wiki = FindWikiPage(self.data_instances, api_search_quantity=self.api_search_quantity)

        print(f"\n ----- Row number {dict_to_find['number']} is searching")

        found = {'number': dict_to_find['number'],
                 'list': find_wiki.search_and_get(raw_data=dict_to_find['list'])}

        return found

    def main_multiproc(self, file_in, file_out, quantity, proc_n):
        """Main Function"""

        start = time.time()

        file = self.open_file(file_in)[0:quantity]
        print(file)
        number = -1

        new_data_list = []
        for data in file:
            number += 1

            new_data_list.append({'number': number,
                                  'list': data})

        pool = multiprocessing.Pool(proc_n)
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


def main():
    config = json.load(open("config.json"))

    readd = ReadWrite(data_instances=config["data_instances"],
                      api_search_quantity=config["api_search_quantity"])
    if config["classify_entities"] == "True":
        if config["classify_entities_method"] == 1:
            from entity_classification import EntityClassification
            classif = EntityClassification()
            new_instances = classif.get_entity_classif(input_data=config["file_in"],
                                                      nrows=config["row_number_to_check"])
            if config["search_after_classification"] == "True":
                readd = ReadWrite(data_instances=new_instances ,
                                  api_search_quantity=config["api_search_quantity"])
                readd.main_multiproc(config["file_in"],
                                     config["file_out"],
                                     config["row_number_to_check"],
                                     proc_n=config["multiprocessing_number"])

        else:
            readd.get_instances_of_raw_data(file_in=config["file_in"],
                                            quantity=config["row_number_to_check"],
                                            with_instance=True)
    else:
        if "multiprocessing_number" == 1:
            readd.main_normal(config["file_in"], config["file_out"], config["row_number_to_check"])
        else:
            if config["multiprocessing_number"] > multiprocessing.cpu_count():
                config["multiprocessing_number"] = multiprocessing.cpu_count()
            readd.main_multiproc(config["file_in"],
                                 config["file_out"],
                                 config["row_number_to_check"],
                                 proc_n=config["multiprocessing_number"])


if __name__ == "__main__":
    main()
    # data_instance = ['Q7187', 'Q8054', 'Q2996394', 'Q14860489', 'Q5058355']
    #
    # readdd = ReadWrite(data_instances=data_instance, api_search_quantity=30)
    #
    # readdd.main_normal("Data\\Input\\input_data1.csv", "Data\\new.csv", 10)
    # readdd.main_multiproc("Data\\Input\\input_data1.csv", "Data\\new.csv", 300)
    #
    # readdd.get_instances_of_raw_data("Data\\Input\\input_data1.csv", 10)
