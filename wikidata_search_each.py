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
    def get_wiki_entities_by_string(self, entity_name):
        params = {'action': 'wbsearchentities',
                  'format': 'json',
                  'language': 'en',
                  'type': 'item',
                  'search': entity_name,
                  "limit": 20}

        response = requests.get(
            WIKI_DATA_API,
            params=params,
        )

        if response.status_code != 200:
            raise Exception("Bad response:(")
        return response.json()

    # getting id of all found items
    def get_wiki_ids_by_string(self, entity_name):
        entities_found = self.get_wiki_entities_by_string(entity_name)
        id_arr = []
        for entity in entities_found["search"]:
            id_arr.append(entity['id'])
        
        return id_arr

    # Given an entity_id, searches for and returns all statements as dictionary. Statements are information that is linked to a wikidata entity.
    def get_wiki_entity_by_id(self, entity_id):
        entity_page = pywikibot.ItemPage(self.repo, entity_id)
        entity_dict = entity_page.get()  # Get the entity page
        
        # ---- Create a well-structured dictionary to our needs
        wiki_relations_dict = dict(entity_dict["claims"])  # Get the claim dictionary
        relations_dict = {}

        for property_id in wiki_relations_dict.keys():
            relations_dict[property_id]  = []

            for wiki_relation in wiki_relations_dict[property_id]:
                wiki_response_dict = wiki_relation.toJSON()
                if (wiki_response_dict['mainsnak']['snaktype'] == 'value') and (wiki_response_dict['mainsnak']['datavalue']['type'] == 'wikibase-entityid'):
                    relations_dict[property_id].append('Q' + str(wiki_response_dict['mainsnak']['datavalue']['value']['numeric-id']))

        return(relations_dict)

    # Searching connections from entity (tail) to entity (head)
    def get_relations_between_two_wikidata_entity_lists(self, tail, head):
        relations = []
        # print(head)
        head_entities = head['found_items']
        tail_entities = tail['found_items']
        for head_entity in head_entities:

            for tail_entity in tail_entities:
                for property_id in tail_entity['statements'].keys():

                    if head_entity['item_id_found'] in tail_entity['statements'][property_id]:
                        relations.append({'item_id': tail_entity['item_id_found'],
                                                'property_id': property_id,
                                                'statement_id': head_entity['item_id_found']})

        return relations

    # input - list of entity lists; output - list of relation lists
    def get_relations_between_wikidata_entity_lists(self, entity_lists):
        list_of_relations = [[] for k in range(len(entity_lists) - 1)]
        for tail_list_id in range(len(entity_lists)):
            for head_list_id in range(len(entity_lists)):
                if tail_list_id < head_list_id: # In this way, all the entity lists are only crossed once.
                    relations = self.get_relations_between_two_wikidata_entity_lists(entity_lists[tail_list_id], entity_lists[head_list_id])

                    reversed_relations = self.add_reversed_tag_to_connections(
                        self.get_relations_between_two_wikidata_entity_lists(entity_lists[head_list_id], entity_lists[tail_list_id]))
                    
                    relations.extend(reversed_relations)

                    list_of_relations[tail_list_id].append(relations)
        return list_of_relations

    # input - list of entity names; output - list of search results
    def get_wiki_entities_by_string_list(self, entity_names):
        relations_lists = []
        for entity_name in entity_names:
            relations_list = []
            if entity_name != '':
                for entity in self.get_wiki_ids_by_string(entity_name):
                    relations_list.append({ "item_id_found": entity,
                                            "statements": self.get_wiki_entity_by_id(entity)})
                relations_lists.append({    'searching item': entity_name,
                                            'found_items': relations_list})
            else:
                relations_lists.append(None)
        return relations_lists

    # combines the different lists of relations to output entity combinations
    def combine_relations(self, lists_of_relations):
        entity_combinations = []
        number_of_entities = len(lists_of_relations) + 1

        # loop over lists of relations  [[(1:2),(1:3)],[(2:3)]]
        for tail_entity in range(number_of_entities - 1): # tail

            # loop over this item connection with each
            for head_entity in range(len(lists_of_relations[tail_entity])): # head

                # loop over connection each item of where connection is found (e.g. 1 with 2 each)
                for head_tail_relation in lists_of_relations[tail_entity][head_entity]: # relation tail-head

                    added = False
                    # loop over list of already chosen items
                    for relation_combination_id in range(len(entity_combinations)):

                        # if id in the list of connections is the same as id of item that is connecting
                        if entity_combinations[relation_combination_id][tail_entity] == head_tail_relation["item_id"]:

                            # checking if cell is not empty or have the same value
                            if entity_combinations[relation_combination_id][tail_entity + head_entity + 1] not in [None, head_tail_relation["statement_id"]]:

                                # adding new list to the list of possible connection and adding new value
                                entity_combinations.append(entity_combinations[relation_combination_id][:])
                                entity_combinations[-1][tail_entity + head_entity + 1] = head_tail_relation[
                                    "statement_id"]

                            else:
                                # adding new new value to existing list
                                entity_combinations[relation_combination_id][tail_entity + head_entity + 1] = head_tail_relation[
                                    "statement_id"]
                            added = True

                        # if id in the list of connections is the same as id of item to which has to be connected
                        # (statement id)
                        if entity_combinations[relation_combination_id][tail_entity + head_entity + 1] == head_tail_relation[
                            "statement_id"]:
                            if entity_combinations[relation_combination_id][tail_entity] not in [None,head_tail_relation["item_id"]]:

                                # adding new list to the list of possible connection and adding new value
                                entity_combinations.append(entity_combinations[relation_combination_id])
                                entity_combinations[-1][tail_entity] = head_tail_relation["item_id"]
                            else:

                                # adding new new value to existing list
                                entity_combinations[relation_combination_id][tail_entity] = head_tail_relation["item_id"]
                            added = True

                    # if value is not added - creating a new list in the list of possible items
                    if not added:
                        entity_combinations.append(self.create_none_list(number_of_entities))
                        entity_combinations[-1][tail_entity] = head_tail_relation["item_id"]
                        entity_combinations[-1][tail_entity + head_entity + 1] = head_tail_relation["statement_id"]

        # choosing only get_unique_values lists
        # entity_combinations = self.get_unique_values(entity_combinations)
        print(f"Possible combinations of entities found: {len(entity_combinations)}")
        return entity_combinations

    # creating a list with None values with length - quantity_of_items
    def create_none_list(self, n):
        return [None for k in range(n)]

    def add_reversed_tag_to_connections(self, relation_list):
        new_list = []
        for relation in relation_list:
            new_list.append(
                {'item_id': relation['statement_id'],
                 'property_id': relation['property_id'] + "R",
                 'statement_id': relation['item_id']}
            )
        return new_list

    # gets list, and returns list with only get_unique_values values
    def get_unique_values(self, original_list):

        # initialize a null list
        unique_list = []

        # traverse for all elements
        for x in original_list:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
        return unique_list

    # getting list of lists of found id and choosing most suitable.
    def choose_most_suitable_wiki_representation(self, candidate_representations):
        list_score = []
        for candidate in candidate_representations:
            if None not in candidate:
                if self.get_unique_values(candidate) == candidate:
                    return candidate
            else:
                list_score.append(self.count_items(candidate, None))
        lowest_value_nb = 0
        lowest_value = len(candidate_representations[0])
        for value in range(len(list_score)):
            if list_score[value] < lowest_value:
                lowest_value_nb = value

        end_list = []
        print("this::")
        print(candidate_representations[lowest_value_nb])
        for item_id in range(len(candidate_representations[lowest_value_nb])):
            if candidate_representations[lowest_value_nb][item_id] is None:
                for possible_item_set in candidate_representations:
                    if possible_item_set[item_id] is not None:
                        end_list.append(possible_item_set[item_id])
                        break
            else:
                end_list.append(candidate_representations[lowest_value_nb][item_id])
            if len(end_list)-1 < item_id:
                end_list.append('')
        print(end_list)
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
            for string_search in range(len(data)):
                if data[string_search] == '':
                    empty_items.append(True)
                else:
                    empty_items.append(False)
                    new_data.append(data[string_search])


            wiki_entities = self.get_wiki_entities_by_string_list(new_data)
            print("############## \n Stepppp 2\n")
            # pprint.pprint(wiki_entities)

            wiki_relations = self.get_relations_between_wikidata_entity_lists(wiki_entities)
            print("############## \n Stepppp 3\n")
            # pprint.pprint(wiki_relations)

            combination_of_relations = self.combine_relations(wiki_relations)
            print("list of possible connections:")
            print("############## \n Stepppp 4\n")
            # pprint.pprint(combination_of_relations)

            most_suitable_wiki_representation = self.choose_most_suitable_wiki_representation(combination_of_relations)

            list_of_results = []
            for empty in empty_items:
                if empty:
                    list_of_results.append('')
                else:
                    list_of_results.append(most_suitable_wiki_representation[0])
                    del most_suitable_wiki_representation[0]

            # print(f"end list: {list_of_results}")

            print(list_of_results)

            end = time.time() - start
            m, s = divmod(end, 60)
            print("Time spent: {} min {} sec.".format(int(m), s))

            return list_of_results
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

    # data = ["Spain", "Barcelona", 'Madrid', 'portugal', 'France']

    data = ['Portugal', "Bacalhau", 'Ronaldo', 'Salazar', 'Madeira']

    # import random
    # random.shuffle(data)
    find_wiki = FindWikiPage()
    output = find_wiki.start(data)
    print(output)

