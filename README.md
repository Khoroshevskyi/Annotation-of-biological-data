# The annotation of biological data and not only. (Wikidata source)


All scripts were developed for python3.x for Windows users (Other platforms are not verified)
###Repo contains 3 scripts: 
## find_file_on_wikidata.py
<br /> Script is mainly responsible for reading files which contains 
information that has to be found, and write the output to another file.<br />

All configurations that script is using can be found in [config.json](config.json)

### Main configurations and paths that have to be specified in [config.json](config.json)</b>:

- <b>*"classify_entities"*</b>
  
If you don't know the instances of each column, you would like to get it, and
to write the id of the instances of to the config file. To do this, you have to 
put *"True"*, and afterward, you have to specify the: <br />
- <b>*"get_possible_output_method"*</b><br />
There are 2 methods, by which we can define columns:
 
    1) Method is searching the instaces_of separately each column, and counting only
         values, where in search output is only one element. <br />
         Config file looks like:
  ```
    "get_possible_output": "True",
    "get_possible_output_method": 2,
    ...
  ```
    The output will be e.g.:
  ```
    {   0: [('Q7187', 486)],
        1: [('Q8054', 318), ('Q66826848', 3), ('Q417841', 1)],
        2: [('Q2996394', 447), ('Q4915012', 2), ('Q30612', 1), ('Q210973', 1), ('Q20732156', 1)],
        3: [('Q14860489', 437), ('Q67015883', 1)],
        4: [('Q5058355', 59), ('Q78155096', 6), ('Q67015883', 1), ('Q67101749', 1)]
    }
  ```
    -  *"search_after_classification"*<br />
write _"True"_ if you want to search after classification and based on classification 
       <br /> <br /> 
       
    2) Method is searching all instances_of of all related items, and then
    counts them. <br />
    Config file looks like:
  ```
    "get_possible_output": "True",
    "get_possible_output_method": 1,
    ...
  ```
    The output will be e.g.:
  ```
            ### numb: 1
            # Q8054 --> 58.33%
            # Q7187 --> 41.67%
            ### numb: 2
            # Q7187 --> 25.0%
            # Q8054 --> 75.0%
            ### numb: 3
            # Q2996394 --> 66.67%
            #  --> 33.33%
            ### numb: 4
            #  --> 83.33%
            # Q14860489 --> 16.67%
            ### numb: 5
            # Q5058355 --> 75.0%
            #  --> 25.0%
  ```
- <b>*"file_in"*</b>

 The Path to the file with input data
 <br /> example input file (input_file): 

```
SCO3114,SCO3114,protein transport,,integral component of membrane
SPy_0779,SPy0779,,,
Serine transporter BC3398,serine transporter BC3398,amino acid transmembrane transport,,integral component of membrane
kdsD,PP_0957,carbohydrate metabolic process,metal ion binding,
smi_1464,smi_1464,,,integral component of membrane
```
The input data can be whatever it is, but every item has to be connected with at least one item.

- <b>*"file_out"*</b>

<br /> Output of the script is file with links:
<br /> *file_example (output_file)*: 

```
http://www.wikidata.org/entity/Q23284357,http://www.wikidata.org/entity/Q27750183,http://www.wikidata.org/entity/Q14860325,,http://www.wikidata.org/entity/Q14327652
http://www.wikidata.org/entity/Q23235634,http://www.wikidata.org/entity/Q23497168,,,
http://www.wikidata.org/entity/Q23196205,http://www.wikidata.org/entity/Q23514357,http://www.wikidata.org/entity/Q14905294,,http://www.wikidata.org/entity/Q14327652
http://www.wikidata.org/entity/Q22311550,http://www.wikidata.org/entity/Q22318912,http://www.wikidata.org/entity/Q2734081,http://www.wikidata.org/entity/Q13667380,
http://www.wikidata.org/entity/Q23235886,http://www.wikidata.org/entity/Q23548717,,,http://www.wikidata.org/entity/Q14327652
```

- <b>*"row_number_to_check"*</b>
  
Specify, how many rows do we want to check in the file

- <b>*"multiprocessing_number"*</b>
  
Specify, how many cores do we want to use to fined related items

- <b>*"api_search_quantity"*</b>
  
Specify, how many items we want to search with wikidata API,
you have to specify value between 1 and 50. The bigger value, better result, but slower it will go.

- <b>*"data_instances"*</b>

Specify, the data instaces for all the clumns, if you know.
If you don't know, you can run program with get_possible_output: "True", 
and find this instaces_of.

It has to look like: 

```
    {
    ... ,
    "data_instances": ["Q7187", "Q8054", "Q2996394", "Q14860489", "Q5058355"]
}
```
Or you can specify it None (if you don't know it)
```
    {
    ... ,
    "data_instances": "None"
}
```


## find_single_row_on_wikidata.py

<br /> Script to find linked data in wikidata. Script uses library: requests and pywikibot to find and 
download data on wikidata portal.

To run the script first, you have to call the class "FindWikiPage":
```
data_instances = ['Q7187', 'Q8054', 'Q2996394', 'Q14860489', 'Q5058355']
find_wiki = FindWikiPage(instances=data_instances, api_search_quantity=30)
```
where instances are the instance_of the item in the wikidata (If not known, write _None_)</br>
api_search_quantity is number of items we want to search in wikidata.

<b>Main Methods in FindWikiPage are:</b>

*search(data)*

Method for searching information about strings, but returning nothing, just remembering information that was found
_data_ - is a list of strings that are related, that we want to find

- *get_answer()*

Method returning ids, that has been found

- *search_and_get(data)*

Method is a combination of 2 methods above

*get_list_of_possible_answers(with_instances=True)*

Method returning all possible answers for this _data_</b>
If yo would like to get all possible answers with instance_of this items, you would have to specify
_with_instances=True_, otherwise: _with_instances=False_

#### Some examples:

- First of all call the class "FindWikiPage":
```
data_instances = ['Q7187', 'Q8054', 'Q2996394', 'Q14860489', 'Q5058355']
find_wiki = FindWikiPage(instances=data_instances, api_search_quantity=15)
```
- Search and get_answers the ids:
```
data1 = ['SCO3114', 'protein transport', '', 'SCO3114', 'integral component of membrane']

find_wiki.search(data1)
output = find_wiki.get_answer()
print(output)
```
The same result will be by using search_and_get()
The return is:
```
['Q23284357', 'Q27750183', 'Q14860325', '', 'Q14327652']
```
- Get all possible answers with instances:
```
    find_wiki.search(data1)
    possible_answers = find_wiki.get_list_of_possible_answers(with_instances=True)
    print("Possible answers are:")
    pprint.pprint(possible_answers)
```
output:
```
Possible answers are:
[{'instances': ['Q8054', 'Q2996394', '', 'Q7187', 'Q5058355'],
  'items': ['Q27750183', 'Q14860325', '', 'Q23284357', 'Q14327652']},
 {'instances': ['Q7187', 'Q2996394', '', 'Q8054', 'Q5058355'],
  'items': ['Q23284357', 'Q14860325', '', 'Q27750183', 'Q14327652']},
 {'instances': ['Q8054', 'Q2996394', '', 'Q8054', 'Q5058355'],
  'items': ['Q27750183', 'Q14860325', '', 'Q27750183', 'Q14327652']}]

```

## check_two_csvs.py

*check_two_csvs(results_path,ground_truth_path)*
  <br /> For given results and ground truth paths, 
  gives a weighted accuracy of the results based on the ground truth. 
  The scoring method is not done per cell, but per row. 
  This method is adjusted to the annotation project where the first two columns are more important than the last three.

To run this program do this:
1) Open [check_two_csvs.py](check_two_csvs.py)
2) Change to your path results_path and ground_truth_path this rows:
```
    check_two_csvs(results_path,
                   ground_truth_path)
```
3) Save and Run program



