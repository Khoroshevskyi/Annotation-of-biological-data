import pywikibot
import requests
import time
import pprint

"""
We can improve code by trying to find items by limit 5 and increasing it !!!! In the search entities
"""

WIKI_DATA_API = 'https://www.wikidata.org/w/api.php'
INSTANCE_OF = 'P31'


class FindWikiPage(object):
    def __init__(self, instances=None, api_search_quantity=20):
        print("FindWikiPage initiated...")
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.repo = self.site.data_repository()

        self.id_with_statements = {}
        self.api_search_quantity = api_search_quantity
        self.instances = instances
        self.raw_data = []
        self.empty_items = []
        self.list_of_possible_answers = []

    # searching items by expressions by using API

    def search_entities(self, entity_name):

        params = {'action': 'wbsearchentities',
                  'format': 'json',
                  'language': 'en',
                  'type': 'item',
                  'search': entity_name,
                  "limit": self.api_search_quantity}


        response = requests.get(
            WIKI_DATA_API,
            params=params,
        )

        if response.status_code != 200:
            raise Exception("Bad response:(")
        return response.json()

    # getting id of all found items
    def get_wiki_ids_by_string(self, entity_name):
        entities_found = self.search_entities(entity_name)
        id_arr = []
        for item in entities_found["search"]:
            id_arr.append(item['id'])
        # print(f"The item ids for {search_item} are:")
        # pprint.pprint(id_arr)
        return id_arr

    # Given an entity_id, searches for and returns all statements as dictionary.
    # Statements are information that is linked to a wikidata entity.
    def get_wiki_relations_by_id(self, entity_id):
        if entity_id in self.id_with_statements.keys():
            return self.id_with_statements[entity_id]

        entity_page = pywikibot.ItemPage(self.repo, entity_id)
        entity_dict = entity_page.get()  # Get the item dictionary


        # ---- Create a well-structured dictionary to our needs
        wiki_relations_dict = dict(entity_dict["claims"])  # Get the claim dictionary
        relations_dict = {}

        for property_id in wiki_relations_dict.keys():
            relations_dict[property_id] = []

            for wiki_relation in wiki_relations_dict[property_id]:
                wiki_response_dict = wiki_relation.toJSON()
                if wiki_response_dict['mainsnak']['snaktype'] == 'value':
                    if wiki_response_dict['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
                        relations_dict[property_id].append(
                            'Q' + str(wiki_response_dict['mainsnak']['datavalue']['value']['numeric-id']))

        self.id_with_statements[entity_id] = relations_dict
        return relations_dict

    # Searching connection in item (search_in) to item (search_item)
    def get_relations_between_2_entities(self, tail, head):
        relations = []
        # print(search_item)
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


    # input - list of string to find; output - list of list of found id's with all statements
    def get_relations_between_few_entities(self, entity_lists):
        list_of_relations = [[] for k in range(len(entity_lists) - 1)]
        for tail_list_id in range(len(entity_lists)):
            for head_list_id in range(len(entity_lists)):
                if tail_list_id < head_list_id:
                    relations = (self.get_relations_between_2_entities(entity_lists[tail_list_id], entity_lists[head_list_id]))

                    reversed_relations = self.add_reversed_tag_to_connections(
                        self.get_relations_between_2_entities(entity_lists[head_list_id], entity_lists[tail_list_id]))

                    relations.extend(reversed_relations)

                    list_of_relations[tail_list_id].append(relations)
        return list_of_relations


    # input - list of list of found id's with all statements; output - list of list connected items and statements
    def get_id_statement_by_list(self, entity_names):

        relations_lists = []
        for entity_name in entity_names:
            relations_list = []
            if entity_name != '':
                for item in self.get_wiki_ids_by_string(entity_name):
                    relations_list.append({"item_id_found": item,
                                             "statements": self.get_wiki_relations_by_id(item)})
                relations_lists.append({'searching item': entity_name,
                                     'found_items': relations_list})

            else:
                relations_lists.append(None)
        return relations_lists


    # combines the different lists of relations to output entity combinations
    def combine_relations(self, lists_of_relations):
        entity_combinations = []
        number_of_entities = len(lists_of_relations) + 1


        # loop on lists of connections  [[(1:2),(1,3)],[(2,3)]]
        for tail_entity in range(number_of_entities - 1):

            # loop on this item connection with each
            for head_entity in range(len(lists_of_relations[tail_entity])):

                # loop on connection each item of where connection is found (e.g. 1 with 2 each)
                for head_tail_relation in lists_of_relations[tail_entity][head_entity]:

                    added = False
                    # loop on list of already chosen items

                    for relation_combination_id in range(len(entity_combinations)):

                        # if id in the list of connections is the same as id of item that is connecting
                        if entity_combinations[relation_combination_id][tail_entity] == head_tail_relation["item_id"]:

                            # checking if cell is not empty or have the same value
                            if entity_combinations[relation_combination_id][tail_entity + head_entity + 1] not in [None, head_tail_relation["statement_id"]]:

                                # adding new list to the list of possible connection and adding new value

                                new_item = entity_combinations[relation_combination_id][:]
                                new_item[tail_entity + head_entity + 1] = head_tail_relation["statement_id"]
                                if new_item not in entity_combinations:
                                    entity_combinations.append(new_item)

                            else:
                                # adding new new value to existing list
                                entity_combinations[relation_combination_id][tail_entity + head_entity + 1] = head_tail_relation["statement_id"]

                            added = True

                        # if id in the list of connections is the same as id of item to which has to be connected
                        # (statement id)
                        if entity_combinations[relation_combination_id][tail_entity + head_entity + 1] == head_tail_relation[
                            "statement_id"]:

                            if entity_combinations[relation_combination_id][tail_entity] not in [None,
                                                                                                 head_tail_relation["item_id"]]:

                                # adding new list to the list of possible connection and adding new value
                                new_item = entity_combinations[relation_combination_id][:]
                                new_item[tail_entity] = head_tail_relation["item_id"]
                                if new_item not in entity_combinations:
                                    entity_combinations.append(new_item)


                            else:

                                # adding new new value to existing list
                                entity_combinations[relation_combination_id][tail_entity] = head_tail_relation["item_id"]
                            added = True

                    # if value is not added - creating a new list in the list of possible items
                    if not added:
                        entity_combinations.append(self.create_none_list(number_of_entities))
                        entity_combinations[-1][tail_entity] = head_tail_relation["item_id"]
                        entity_combinations[-1][tail_entity + head_entity + 1] = head_tail_relation["statement_id"]


        # choosing only unique lists
        # list_of_possible_connections = self.get_unique_values(list_of_possible_connections)
        print(f"Possible items found: {len(entity_combinations)}")

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


    # counting quantity of specific item in the list
    def count_items(self, list_of_items, x):
        count = 0
        for ele in list_of_items:
            if ele == x:
                count += 1
        return count

    def join_ids_with_instances(self):
        join_instances_list = []
        for possible_list in self.list_of_possible_answers:
            items_with_instances = []
            for each_item in possible_list:
                try:
                    items_with_instances.append(self.id_with_statements[each_item][INSTANCE_OF][0])
                except KeyError:
                    items_with_instances.append('Q0')

            join_instances_list.append({'items': self.fill_empty_items(possible_list),
                                        'instances': self.fill_empty_items(items_with_instances)})

        # pprint.pprint(join_instances_list)
        return join_instances_list

    def get_list_of_possible_answers(self, with_instances=False):
        if with_instances:
            return self.join_ids_with_instances()
        else:
            return self.list_of_possible_answers

    # getting list of lists of found id and choosing most suitable
    def choose_most_suitable(self, list_of_possible_item_set):
        list_score = []
        for possible_item_set in list_of_possible_item_set:
            if None not in possible_item_set:
                if self.get_unique_values(possible_item_set) == possible_item_set:
                    return possible_item_set

            else:
                list_score.append(self.count_items(candidate, None))
        lowest_value_nb = 0
        lowest_value = len(candidate_representations[0])
        for value in range(len(list_score)):
            if list_score[value] < lowest_value:
                lowest_value_nb = value

        end_list = []
        # print(list_of_possible_item_set[lowest_value_nb])
        for item_id in range(len(list_of_possible_item_set[lowest_value_nb])):
            if list_of_possible_item_set[lowest_value_nb][item_id] is None:
                for possible_item_set in list_of_possible_item_set:

                    if possible_item_set[item_id] is not None:
                        end_list.append(possible_item_set[item_id])
                        break
            else:

                end_list.append(list_of_possible_item_set[lowest_value_nb][item_id])
            if len(end_list) - 1 < item_id:

                end_list.append('')
        # print(end_list)
        return end_list

    def get_best_id_by_known_instances(self):
        # new = self.instances and self.empty_items
        # reversing empty_items
        empty_items_reverse = [not elem for elem in self.empty_items]

        # deleting instances if there is no values
        instances_adjusted = [b and a for a, b in zip(self.instances, empty_items_reverse)]
        instances_adjusted = list(filter(bool, instances_adjusted))
        # print(instances_adjusted)

        ids_with_instances = self.join_ids_with_instances()
        for possible_answ in ids_with_instances:
            if possible_answ['instances'] == instances_adjusted:
                return possible_answ['items']

            if sorted(possible_answ['instances']) == sorted(instances_adjusted):
                list_to_return = []
                for correct in range(len(instances_adjusted)):
                    for item_to_sort in range(len(possible_answ['instances'])):
                        if instances_adjusted[correct] == possible_answ['instances'][item_to_sort]:
                            list_to_return.append(possible_answ['items'][item_to_sort])
                            break
                return list_to_return

        print('#################')
        return self.choose_most_suitable(self.list_of_possible_answers)

    def get_answer(self):
        try:
            if self.instances is not None:
                values_for_return = self.get_best_id_by_known_instances()
            else:
                values_for_return = self.choose_most_suitable(self.list_of_possible_answers)
            return self.fill_empty_items(values_for_return)
        except Exception as err:
            print(f'in: get_most_answer has occurred an error, {err}')
            return ['' for x in range(len(self.empty_items))]

    def delete_empty_items(self, data):
        self.empty_items = []
        new_data = []
        for string_search in range(len(data)):
            if data[string_search] == '' or data[string_search] is None:
                self.empty_items.append(True)
            else:
                self.empty_items.append(False)
                new_data.append(data[string_search])
        return new_data

    def fill_empty_items(self, found_data):
        end_list = []
        found_data_new = found_data[:]
        for empty in self.empty_items:
            if empty:
                end_list.append('')
            else:
                end_list.append(found_data_new[0])
                del found_data_new[0]
        return end_list

    # starts the script with finding items and checking if they are connected
    def search(self, raw_data):

        self.raw_data = raw_data
        try:
            start = time.time()

            # we have empty items - deleting them, but remembering where they were:
            new_data = self.delete_empty_items(raw_data)

            wiki_entities = self.get_wiki_entities_by_string_list(new_data)
            print("############## \n Stepppp 2\n")
            # pprint.pprint(wiki_entities)

            list_of_connections = self.get_relations_between_few_entities(list_item_id)
            # print("############## \n Stepppp 3\n")
            # pprint.pprint(list_of_connections)

            self.list_of_possible_answers = self.combine_relations(list_of_connections)
            # print("list of possible connections:")
            # print("############## \n Stepppp 4 : self.list_of_possible_answers:\n")
            # pprint.pprint(self.list_of_possible_answers)


            end = time.time() - start
            m, s = divmod(end, 60)
            print("Time spent on searching: {} min {} sec.".format(int(m), s))




if __name__ == "__main__":

    # sample row_data
    data1 = ['amino acid transmembrane transport',
            'Serine transporter BC3398',
            'serine transporter BC3398',
            'integral component of membrane', '']
    data_instances = ['Q7187', 'Q8054', 'Q2996394', 'Q14860489', 'Q5058355']

    # row_data = ['SE2280', 'transcription-repair coupling factor', "regulation of transcription, DNA-templated",
    #         'hydrolase activity', 'cytoplasm']

    find_wiki = FindWikiPage(data_instances, api_search_quantity=25)
    find_wiki.search(data1)


    possible_answers = find_wiki.get_list_of_possible_answers(with_instances=True)
    print("Possible answers are:")
    print(possible_answers)

    output = find_wiki.get_answer()
    print("Best answer is:")
    print(output)
