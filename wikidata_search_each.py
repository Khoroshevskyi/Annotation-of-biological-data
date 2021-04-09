import pywikibot
import requests
import time
import pprint

"""
We can improve code by trying to find items by limit 5 and increasing it !!!! In the search entities
"""

WIKI_DATA_API = 'https://www.wikidata.org/w/api.php'


class FindWikiPage(object):
    def __init__(self):
        print("FindWikiPage initiated...")
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.repo = self.site.data_repository()

    # searching items by expressions by using API
    def search_entities(self, itemtitle):
        params = {'action': 'wbsearchentities',
                  'format': 'json',
                  'language': 'en',
                  'type': 'item',
                  'search': itemtitle,
                  "limit": 30}

        response = requests.get(
            WIKI_DATA_API,
            params=params,
        )

        if response.status_code != 200:
            raise Exception("Bad response:(")
        return response.json()

    # getting id of all found items
    def get_search_ids(self, search_item):
        id_found = self.search_entities(search_item)
        id_arr = []
        for item in id_found["search"]:
            id_arr.append(item['id'])
        # print(f"The item ids for {search_item} are:")
        # pprint.pprint(id_arr)
        return id_arr

    # Getting item_id and searching for all statements with values than returns dict:
    # Dict looks like: (example)
    # {'P1343': ['Q30039501'],
    # 'P279': ['Q2449730', 'Q8054'],
    # 'P31': ['Q8054'],...}
    def get_statements(self, item_identifier):
        item = pywikibot.ItemPage(self.repo, item_identifier)
        item_dict = item.get()  # Get the item dictionary
        clm_dict = dict(item_dict["claims"])  # Get the claim dictionary
        dict_of_properties = {}

        for property_id in clm_dict.keys():
            dict_of_properties[property_id]  = []

            for clm in clm_dict[property_id]:
                response_dict = clm.toJSON()
                if response_dict['mainsnak']['snaktype'] == 'value':
                    if response_dict['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
                        dict_of_properties[property_id].append('Q' + str(response_dict['mainsnak']['datavalue']['value']['numeric-id']))

        return(dict_of_properties)

    # Searching connection in item (search_in) to item (search_item)
    def find_items_connections(self, search_in, search_item):
        connected_items = []
        # print(search_item)
        search_item = search_item['found_items']
        search_in = search_in['found_items']
        for each_found_search_item in search_item:

            for each_found_search_in_item in search_in:
                for property_id in each_found_search_in_item['statements'].keys():

                    if each_found_search_item['item_id_found'] in each_found_search_in_item['statements'][property_id]:
                        connected_items.append({'item_id': each_found_search_in_item['item_id_found'],
                                                'property_id': property_id,
                                                'statement_id': each_found_search_item['item_id_found']})

        return connected_items

    # input - list of string to find; output - list of list of found id's with all statements
    def get_list_of_connections(self, list_item_id):
        list_of_connections = [[] for k in range(len(list_item_id) - 1)]
        for first in range(len(list_item_id)):
            for second in range(len(list_item_id)):
                if first < second:
                    small_list = (self.find_items_connections(list_item_id[first], list_item_id[second]))

                    reversed_list = self.change_item_statement(
                        self.find_items_connections(list_item_id[second], list_item_id[first]))
                    small_list.extend(reversed_list)

                    # print(f"{first}-->{second}::")
                    # pprint.pprint(small_list)

                    list_of_connections[first].append(small_list)
        return list_of_connections

    # input - list of list of found id's with all statements; output - list of list connected items and statements
    def get_id_statement_by_list(self, data):
        list_item_id = []
        for search_item in data:
            list_of_found_id = []
            if search_item != '':
                for item in self.get_search_ids(search_item):
                    list_of_found_id.append({"item_id_found": item,
                                             "statements": self.get_statements(item)})
                list_item_id.append({'searching item': search_item,
                                     'found_items': list_of_found_id})
            else:
                list_item_id.append(None)
        return list_item_id

    # list of items connected
    def each_item_connections(self, list_of_list_connections):
        list_of_possible_connections = []
        quantity_of_items = len(list_of_list_connections) + 1

        item_connections = 0
        # loop on lists of connections  [[(1:2),(1,3)],[(2,3)]]
        for item_connections in range(quantity_of_items - 1):

            # loop on this item connection with each
            for con_number in range(len(list_of_list_connections[item_connections])):

                # loop on connection each item of where connection is found (e.g. 1 with 2 each)
                for zero_1 in list_of_list_connections[item_connections][con_number]:

                    added = False
                    # loop on list of already chosen items
                    for pos_con_nb in range(len(list_of_possible_connections)):

                        # if id in the list of connections is the same as id of item that is connecting
                        if list_of_possible_connections[pos_con_nb][item_connections] == zero_1["item_id"]:

                            # checking if cell is not empty or have the same value
                            if list_of_possible_connections[pos_con_nb][item_connections + con_number + 1] not in [None, zero_1["statement_id"]]:

                                # adding new list to the list of possible connection and adding new value
                                list_of_possible_connections.append(list_of_possible_connections[pos_con_nb][:])
                                list_of_possible_connections[-1][item_connections + con_number + 1] = zero_1[
                                    "statement_id"]

                            else:
                                # adding new new value to existing list
                                list_of_possible_connections[pos_con_nb][item_connections + con_number + 1] = zero_1[
                                    "statement_id"]
                            added = True

                        # if id in the list of connections is the same as id of item to which has to be connected
                        # (statement id)
                        if list_of_possible_connections[pos_con_nb][item_connections + con_number + 1] == zero_1[
                            "statement_id"]:
                            if list_of_possible_connections[pos_con_nb][item_connections] not in [None,zero_1["item_id"]]:

                                # adding new list to the list of possible connection and adding new value
                                list_of_possible_connections.append(list_of_possible_connections[pos_con_nb])
                                list_of_possible_connections[-1][item_connections] = zero_1["item_id"]
                            else:

                                # adding new new value to existing list
                                list_of_possible_connections[pos_con_nb][item_connections] = zero_1["item_id"]
                            added = True

                    # if value is not added - creating a new list in the list of possible items
                    if not added:
                        list_of_possible_connections.append(self.create_none_list(quantity_of_items))
                        list_of_possible_connections[-1][item_connections] = zero_1["item_id"]
                        list_of_possible_connections[-1][item_connections + con_number + 1] = zero_1["statement_id"]

        # choosing only unique lists
        # list_of_possible_connections = self.unique(list_of_possible_connections)
        print(f"Possible items found: {len(list_of_possible_connections)}")
        return list_of_possible_connections

    # creating a list with None values with length - quantity_of_items
    def create_none_list(self, quantity_of_items):
        return [None for k in range(quantity_of_items)]

    def change_item_statement(self, list_of_connections):
        new_list = []
        for connection in list_of_connections:
            new_list.append(
                {'item_id': connection['statement_id'],
                 'property_id': connection['property_id'] + "R",
                 'statement_id': connection['item_id']}
            )
        return new_list

    # gets list, and returns list with only unique values
    def unique(self, list_original):

        # initialize a null list
        unique_list = []

        # traverse for all elements
        for x in list_original:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
        return unique_list

    # getting list of lists of found id and choosing most suitable
    def choose_most_suitable(self, list_of_possible_item_set):
        list_score = []
        for possible_item_set in list_of_possible_item_set:
            if None not in possible_item_set:
                if self.unique(possible_item_set) == possible_item_set:
                    return possible_item_set
            else:
                list_score.append(self.count_items(possible_item_set, None))
        lowest_value_nb = 0
        lowest_value = len(list_of_possible_item_set[0])
        for value in range(len(list_score)):
            if list_score[value] < lowest_value:
                lowest_value_nb = list_score
        end_list = []
        for item_id in range(len(list_of_possible_item_set[list_score])):
            if list_of_possible_item_set[list_score][item_id] is None:
                for possible_item_set in list_of_possible_item_set:
                    if possible_item_set[item_id] is not None:
                        end_list.append(possible_item_set[item_id])
                        break
            else:
                end_list.append(list_of_possible_item_set[list_score][item_id])

        return end_list

    # counting quantity of specific item in the list
    def count_items(self, list_of_items, x):
        count = 0
        for ele in list_of_items:
            if (ele == x):
                count += 1
        return count

    # starts the script with finding items and checking if they are connected
    def start(self, data):
        try:
            start = time.time()
            print(data)
            # we have empty items - not check them:
            empty_items = []
            new_data = []
            print(data)
            for string_search in range(len(data)):
                if data[string_search] == '':
                    empty_items.append(True)
                else:
                    empty_items.append(False)
                    new_data.append(data[string_search])


            list_item_id = self.get_id_statement_by_list(new_data)
            # print("############## \n Stepppp 2\n")
            # pprint.pprint(list_item_id)



            list_of_connections = self.get_list_of_connections(list_item_id)
            # print("############## \n Stepppp 3\n")
            # pprint.pprint(list_of_connections)

            list_of_possible_items = self.each_item_connections(list_of_connections)
            print("list of possible connections:")
            # print("############## \n Stepppp 4\n")
            # pprint.pprint(list_of_possible_items)

            found_list = self.choose_most_suitable(list_of_possible_items)
            # print(f"end list: {end_list}")

            end_list = []
            for empty in empty_items:
                if empty:
                    end_list.append('')
                else:
                    end_list.append(found_list[0])
                    del found_list[0]

            print(end_list)

            end = time.time() - start
            m, s = divmod(end, 60)
            print("Time spent: {} min {} sec.".format(int(m), s))

            return end_list
        except Exception as err:
            print(f"Fatal error {err}")
            print(['' for d in range(len(data))])
            return ['' for d in range(len(data))]


if __name__ == "__main__":
    ## sample data
    # data = ['SCO3114','SCO3114','protein transport','integral component of membrane']
    # data = ['SPy_0779','SPy0779']
    # data = ['Serine transporter BC3398',
    #         'serine transporter BC3398',
    #         'amino acid transmembrane transport',
    #         'integral component of membrane','']

    data = ["Spain", "Barcelona", 'Madrid', 'portugal', 'France']

    # import random
    # random.shuffle(data)
    find_wiki = FindWikiPage()
    output = find_wiki.start(data)
    print(output)

