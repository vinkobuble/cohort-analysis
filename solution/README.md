# Cohort Analysis Script

Cohort Analysis is a Python 3.7 script that processes two input CSV files, one containing customers and the other containing orders data.
The output of the script is CSV file with customers usage analytics (count of orders, and percentage of orders) separated in a weekly cohorts.

## How to run script

### Requirements 

The only requirements for script is having Python 3.7.x. 

### Execute

To get list of all cli arguments run

`python3 path/to/solution/directory --help` or `python3 path/to/solution/directory -h`.

CL example if your current dir is `solution`: 

`python3 . -cf ../assignment/customers.csv -of ../assignment/orders.csv -tz Americas/New_York`



