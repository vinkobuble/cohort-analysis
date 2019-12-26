# Invitae coding assignment - Cohort Analysis

__by Vinko Buble, Dec, 2019__

This assignment is a part of candidate is Vinko Buble interview process for Senior Software Engineer position for Invitae, Inc.

## Cohort Analysis Script

Cohort Analysis is a Python 3.7 script that processes two input CSV files, one containing customers and the other containing orders data.
The output of the script is a CSV file with customers cohorts usage analytics per week:
 1. count of unique users in a cohort.
 1. count and percentage percentage of unique users in a week.
 1. count and percentage of 1st time users in a week.
 
 The sample input CSV files can be found in the [data]() folder.
 

## How to run script

### Docker

The safest way the script will run is to start it inside a Docker container.

From the project root folder, where the `Dockerfile` is located, run:

```
docker build -t cohort-analysis . 
```

If you cloned the repo in `Downloads` folder and extracted it there then execute:
```
docker run --rm -v ~/Downloads/vinko-buble-invitae-cohort-analysis/data:/data -ti cohort-analysis python . --customers-file /data/customers.csv --orders-file /data/orders.csv --timezone -0800 --output-file /data/output.csv
```
Or change the path `~/Downloads/vinko-buble-invitae-cohort-analysis` to be the absolute repo path.
 
There are already sample files in [data]() folder inside the project folder.

The script will generate `output.csv` file inside the [data]() folder.


#### Run tests

```
docker run --rm -v ~/Downloads/vinko-buble-invitae-cohort-analysis/data:/data -ti cohort-analysis python -m unittest
```



### Python

#### Requirements 

The only requirement for script is Python 3.7.x. No other dependecy has been added.

#### Execute

To get list of all cli arguments run (change `path/to/solution/directory` for the true path to the `solution` folder)

`python3 path/to/solution/directory --help` or `python3 path/to/solution/directory -h`.

Run the script with input files within the [data]() folder.

`python3 path/to/solution/directory --customers-file ../data/customers.csv --orders-file ../data/orders.csv --timezone -0800 --output-file ../data/output.csv`

#### Running tests

From the `solution` folder run:

```python3 -m unittest```


## Solution

The calculation of the report consists of four stages: 
1. Generate cohort customer ID tree out of customers CSV file [cohort_customer_segment_tree.py](./src/cohort_customer_segment_tree.py)
2. Prepare customer ID -> cohort ID lookup - resolve cohort ID by customer ID. [customer_cohort_index.py](./src/customer_cohort_index.py)
3. Reading orders CSV file, and aggregating the statistics. [cohort_statistics.py](./src/cohort_statistics.py)
4. Generating report - output to CSV file. [report_generator.py](./src/report_generator.py)

### Cohort customer ID tree

The core idea behind implementation of the tree is preserving the memory footprint while improving the time complexity of the alorithm.

This cohort algorithm assumes that function
f(Customers ID) = Customer Creation Date/Time
is almost monotonic and continuous.

**Note**: The test uses following notations: 
- `N` is number of customers, 
- `M` is number of orders, 
- `K` is number of cohorts,
- `S` is maximum number of segments per cohort.

In the case of monotonic continuous function, segments of Customer IDs would be disjunct, each cohort would have only one segment, and the algorithm of building it would consist only of searching for `[min, max]` customer ID values for each cohort: time complexity `O(N)`, space complexity `O(K)`. Then an index for mapping Customer ID to Cohort ID is just a searchable list of customer ID segments.

Since we have an almost monotonic continuous function (very few customer IDs are out of the order),
our structure will have more than one segment of customer IDs per cohort, but not as close as if the customer set is random. Therefore we use trees to represent cohort customer ID segments as the structure that would produce the minimal time and space complexity.

Time Complexity of this step is `O(NlogS)`.
Space complexity is `O(K*S)`.

Otherwise, if list was used, the complexity of `insert` and `del` list operations would produce an algorithm with the `O(N^2/K)` complexity.

As the last step we flatten the structure to get sorted list of customer ID segments for fast lookup by customer ID. 
Time complexity of this step is `O(K*S)`, since it is only traversing through the trees and collecting segments. You can imagine this step as 'balancing the trees'.

The visual presentation of the tree structure:

![Cohort CustomerID segments tree](./assets/cohort-customer-segments-tree.png "Cohort CustomerID segments tree")


### Prepare customer ID -> cohort ID lookup

In this step we take dictionary with cohort segments trees, and construct the list of root nodes. 
Then this list is sorted by the lowest customer ID in the cohort. 

The end result is `K` lists (one per each cohort), and maximum `S` segments per cohort list. Both lists are sorted and binary search can be used for lookups. 

This way we achieve customer ID lookup time complexity of `O(logK x logS)`.


### Aggregating statistics from orders file

Now the script reads the orders file, and finds minimum and maximum weeks for the cohort, and collects customers for each week in sets. 
This is the trickiest part, since no space complexity optimization better than `O(M)` could be found.

The reason for collection all users per week and keeping them in the memory is coming from the requirement to find first-time orderers. 
The only way to count first time orderers is to maintain the unique set of customers per week, and calculate set difference between the current week customers and all customers in the previous weeks.
And this step has to be done after all orders have been processed.

There is `--max_weeks` CLI argument to limit number of weeks to process in the cases where there is more data than available memory.

The time complexity of this step is `O(M x logS x logC)` - for each order we need to perform customer ID lookup to find which cohort the customer belongs.

### Generating report - output CSV file

The simplest of all steps. Take aggregated statistics and cohorts infos, and write the data out in CSV file. 
The time complexity is `O(C x W)` where C is the number of cohorts, and W is the number of weeks.
The space complexity is `O(1)`, if we take into consideration that all needed memory is allocated in the previous step (and not counting the output file as a memory consumer).


