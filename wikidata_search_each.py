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
                  "limit": 20}

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
            dict_of_properties[property_id] = []

            for clm in clm_dict[property_id]:
                response_dict = clm.toJSON()
                if response_dict['mainsnak']['snaktype'] == 'value':
                    if response_dict['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
                        dict_of_properties[property_id].append('Q' + str(response_dict['mainsnak']['datavalue']['value']['numeric-id']))

        return(dict_of_properties)

    # Searching if in the item (search_in) is statement value(id) (search_item)
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

    # For our specific problem -- searching all items by using 2 value from the column
    def for_specific_our_question(self, list_item_id):

        item10 = self.find_items_connections(list_item_id[1], list_item_id[0])

        list_of_items = []
        if list_item_id[2] is not None:
            item12 = self.find_items_connections(list_item_id[1], list_item_id[2])
            list_of_items.append(item12)
        else:
            item12 = ''
        if list_item_id[3] is not None:
            item13 = self.find_items_connections(list_item_id[1], list_item_id[3])
            list_of_items.append(item13)
        else:
            item13 = ''
        if list_item_id[4] is not None:
            item14 = self.find_items_connections(list_item_id[1], list_item_id[4])
            list_of_items.append(item14)
        else:
            item14 = ''

        ids = None

        for a1 in item10:
            if len(list_of_items) != 0:
                ids = self.check_if_the_same(a1['item_id'], list_of_items)
                if ids is not None:
                    ids.insert(0, a1['item_id'])
                    ids.insert(0, a1['statement_id'])
                    break
            else:
                ids = [a1['statement_id'], a1['item_id']]

                break

        if ids is None:
            return None

        if item12 == '':
            ids.insert(2, '')
        if item13 == '':
            ids.insert(3, '')
        if item14 == '':
            ids.insert(4, '')

        return ids

    # searching if protein is in the list of items by using recursive programming
    def check_if_the_same(self, protein, list_of_items):
        for k in list_of_items[0]:
            if protein == k['item_id']:
                if len(list_of_items[1:]) > 0:
                    last_list = self.check_if_the_same(protein, list_of_items[1:])
                    if last_list is not None:
                        last_list.insert(0,  k['statement_id'])
                        return last_list
                else:
                    return [k['statement_id']]

        return None

    # starts the script with finding items and checking if they are connected
    def start(self, data):
        start = time.time()
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

        # pprint.pprint(list_item_id)
        '''
        # ## There has to be some clever algorithm, but no-one knows, how to do it;(
        # ## What we have to do:
        # ## find values from 5 columns that are connected in the best way
        # ## We have list of lists of conected item column by column...
        #
        # list_of_connections = []
        #
        # for first in range(len(list_item_id)):
        #     for second in range(len(list_item_id)):
        #         if first != second:
        #             list_of_connections.append(self.find_if_items_connected(list_item_id[first], list_item_id[second]))
        #             print(f"{first}-->{second}::")
        #             print(self.find_if_items_connected(list_item_id[first], list_item_id[second]))
        # self.search_for_most_popular(list_of_connections)
        '''

        ids = self.for_specific_our_question(list_item_id)

        if ids is None:
            list_item_id[0], list_item_id[1] = list_item_id[1], list_item_id[0]
            ids = self.for_specific_our_question(list_item_id)
        end = time.time() - start

        m, s = divmod(end, 60)
        print("Time spent: {} min {} sec.".format(int(m), s))

        if ids is None:
            return ['', '', '', '', '']
        else:
            return ids

    '''
    # This method has to search the most popular chain: I don't know how to do it :(((
    def search_for_most_popular(self, list_of_connections):
        new_dict = {}
        for dd in list_of_connections:
            for d in dd:
                if d['item_id'] not in new_dict:
                    new_dict[d['item_id']] = 1
                else:
                    new_dict[d['item_id']] += 1

        print(new_dict)
        for dd in list_of_connections:
            print(dd)
    '''


if __name__ == "__main__":
    # correct data:
    data = ["mitochondrial import receptor subunit TOM40, putative","PKH_113200","protein import into mitochondrial matrix",
            "protein transmembrane transporter activity","mitochondrial outer membrane"]
    # data = ["nrdF", "nrdF", "deoxyribonucleotide biosynthetic process",
    #         "ribonucleoside-diphosphate reductase activity, "
    #         "thioredoxin disulfide as acceptor", "membrane"]
    find_wiki = FindWikiPage()
    dd = find_wiki.start(data)
    print(dd)
    # ss = find_wiki.get_statements('Q59983165')
    # pprint.pprint(ss)

