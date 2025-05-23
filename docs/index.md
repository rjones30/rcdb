## RCDB

Run Configuration/Conditions Database (RCDB) stores experiments run related information and conditions. It uses MySQL or SQLite databases to store information about runs and provides interfaces to search runs, manage data, automatic CODA integration, etc. 

The interfaces available are:
- Web site
- Command line interface (CLI)
- Python API
- C++ API
- Possibly JAVA API


#### Demo:

One can visit HallD RCDB Web site as demo:
https://halldweb.jlab.org/rcdb/

Daily updated SQLite database is available here:
https://halldweb.jlab.org/dist/rcdb.sqlite


## Conditions

Run conditions is the way to store information related to a run (which is identified by run_number everywhere).
From a simplistic point of view, run conditions are presented in RCDB as **name**-**value** pairs attached to a run number. For example, **event_count** = **1663** for run **100**.

One of the major use cases of RCDB is searching for runs matching required conditions. 
It is done using simple, python-if-like queries. 
The result of ```event_count > 100000``` is all runs, that, as one would expect, 
have **event_count** more than **100000**

Let's see how API-s would look for the examples above.

Python:
```python
import rcdb

# Open SQLite database connection
db = rcdb.RCDBProvider("sqlite:///path.to.file.db")

# Read value for run 100
event_count = db.get_condition(100, "event_count").value

# Select runs 
table = db.select_values(['polarization_angle','beam_current'], "event_count > 500", run_min=30000, run_max=30050)
for row in table:
   print(row)   # Or do whatever you want with runs
```

CLI:

```bash
export RCDB_CONNECTION=mysql://rcdb@localhost/rcdb
rcdb --help                            # Gives you self descriptive help
rcdb 1000 event_count                  # See exact value of 'event_count' for run 1000
rcnd --write 1663 100 event_count      # Write condition value to run 100
rcnd --search "event_count > 500"      # Select runs 

```


What RCDB conditions are not designed for? - They are not designed for large data sets that change rarely (value is the same for many runs).
That is because each condition value is independently saved (and attached) for each run.

In the case of bulk data, it is better to save it using other RCDB options. RCDB provides the files saving mechanism as example.