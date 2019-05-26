# pydarn
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![GitHub version](https://badge.fury.io/gh/boennemann%2Fbadges.svg)](http://badge.fury.io/gh/boennemann%2Fbadges)

SuperDARN data visualization library. 

## Getting Started 

The following instructions will allow you to install and give some examples on how to use pydarn. 

### Prerequisites

**python 3.6+**

| Ubuntu      | OpenSuse       | Fedora        |
| ----------- | -------------- | ------------- |
| libyaml-dev | python3-PyYAML | libyaml-devel |

You can check your python version with  
`$ python --version` or 
`$ python3 --version`
### Installing 

1. Clone git repository:   
   `git clone https://github.com/SuperDARN/pydarn.git`

2. Installing pydarn  
    1. **Recommended**: Installing a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/), this option allows the library to install needed version of libraries without affecting system libraries.  
        * First install the environment:  
      `$ python3 -m pip install --user virtualenv`  
      `$ python3 -m virtualenv <environment name>`  
		  `$ source <environment name>/bin/activate`
        * Navigate to where you cloned pydarn:  
		  `$ python3 setup.py install`
    2. Install in the system (root privileges required):  
		   `$ sudo python3 setup.py install`

### Examples

#### Reading DMAP file 
The following example shows how to read in a FITACF file, one of the SuperDARN's DMAP file types. 

```python
import pydarn
dmap_file = "./20180410.C0.sas.fitacf"
dmap_reader = pydarn.DmapRead(dmap_file)
dmap_data = dmap_reader.read_records() 

# dmap_data[record number][paramter name].value
print(dmap_data[0]['bmnum'].value) 
```

#### Turn on debugging 

```python
import pydarn
import logging

pydarn_logger = logging.getLogger('pydarn').setLevel(logging.DEBUG)

dmap_file = "./20180410.C0.sas.fitacf"
damp_reader = pydarn.DmapRead(dmap_file)
dmap_data = dmap_reader.read_records() 

print(dmap_data[0]['origin.time'].value) 
```
Run the code and two log files will be produced:
  * pydarn.log - DEBUG level info 
  * pydarn_error.log - ERROR level info

### Release History 

  * 0.0.1 
    * Add: Pydmap DmapRead implemented.