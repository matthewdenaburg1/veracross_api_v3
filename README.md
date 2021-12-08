# Veracross API Python Library

Provides an easy way to pull information from the Veracross' v3 API in Python.

Rate limiting and pagination will be handled automatically.

The API uses OAuth2 for access control. See the [documentation][docs] for more 
information.

## Install

Clone the package and `cd` into the directory you downloaded to.
```bash
git clone https://bitbucket.org/ssfs_tech/veracross_api_v3
cd /path/to/download/directory
```

Install the local version to ensure the most recent updates
```bash
pip3 install .
```

## Example Usage

```python
import json
import sys
import veracross_api

school_short_name = "short"
id_ = "my_id"
secret = "my_secret"
scopes = ["students:list"]

# retrieve the data
v = veracross_api.Veracross(school_short_name, id_, secret, scopes)
data = v.pull("students")

# save the data
with open("students.sample.json", "w") as data_out:
    json.dump(data, data_out)

# print
json.dump(veracross_api.insert_from_value_list(**data), sys.stdout)
```

[docs]: https://api-docs.veracross.com/docs/docs/docs/concepts/general-principles.md
