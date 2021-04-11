import pandas as pd
import numpy as np

def check_two_csvs(results_path,ground_truth_path):
    '''
    Checks whether the csv file specified in the the [results_path] matches the csv file specified in the [ground_truth_path]. Returns a percentage of rows that are equal and a list of the csv file rows that are not equal.

    If files don't have same number of rows, it looks only at the number of row available in the [results_path] csv. Scoring is done per row, where the first two columns are more important. 
    '''    
    results = pd.read_csv(results_path,header=None)
    ground_truth = pd.read_csv(ground_truth_path,header=None)

    num_of_results = len(results.index)
    ground_truth = ground_truth.iloc[0:num_of_results]

    # Only looking at last part of the uris as they subgroups don't match
    results = results.apply(lambda x: x.apply(last_part_of_uri))
    ground_truth = ground_truth.apply(lambda x: x.apply(last_part_of_uri))

    scores = np.zeros(num_of_results)
    wrong_results = list()

    for i in range(num_of_results):
        score = score_rows(results.loc[i],ground_truth.loc[i])
        scores[i] = score
        if (score != 1):
            wrong_results.append(i+1)

    percentage_rows_correctly_labelled = round((scores.sum() / num_of_results) * 100,2)

    print(percentage_rows_correctly_labelled, '%')
    print(wrong_results)

    return percentage_rows_correctly_labelled,wrong_results


def score_rows(row1,row2):
    first_two_columns_equal = (row1[0] == row2[0]) & (row1[1] == row2[1])
    first_two_switched_around = (row1[0] == row2[1]) & (row1[0] == row2[1])
    rest_of_row_equal = (row1[2] == row2[2]) & (row1[3] == row2[3]) & (row1[4] == row2[4])

    if (first_two_columns_equal & rest_of_row_equal):
        return 1
    elif (first_two_switched_around & rest_of_row_equal):
        return 0.75
    elif (first_two_columns_equal & (not rest_of_row_equal)):
        return 0.5
    elif (first_two_switched_around & (not rest_of_row_equal)):
        return 0.25
    else:
        return 0

def last_part_of_uri(uri):
    try:
        uri_parts = uri.split('/')
        last_part = uri_parts[-1]
        stripped_last_part = last_part
    except:
        # print(uri)
        return ''

    return last_part

def check_only_last_part_of_uri(uri1,uri2):
    uri1_last_part = last_part_of_uri(uri1)
    uri2_last_part = last_part_of_uri(uri2)

    last_part_is_equal = uri1_last_part == uri2_last_part

    return last_part_is_equal


if __name__ == "__main__":
    check_two_csvs("Data\\new.csv",
                        "Data\\Ground Truth\\gt_data1.csv")