# Style Guidelines 

To obtain one of pyDARN's software goals, **maintainability**, consistency and following best practices is a requirement. Consistency is set by design choices, standards. 
Because of the advances in programming languages, best practices, features, direction, and libraries, the style guidelines should be reviewer at least once a year. 
When a guideline is put into question due to a new change, then developers should try to meet and discuss a potential change in the guidelines. 

In terms of [code reviews](developer/code_reviewes.md), the style guidelines rule over other style guidelines for the language. Please make sure to follow them. 

## Design Choices 


### Software Design Patterns
pyDARN as an object-oriented (OO) library. Please avoid single functions for interfacing with users. Look into `staticmethods` and `classmethods` if you want a function style call. 
OO design is picked based on fitting the design patterns described lower and to allow for future extendability internal and external of pyDARN. 

#### IO (SuperIO/SDARNIO)
The IO packages should currently follow an **abstraction factory** style of design and an **adaptor** style for conversions between legacy formats and newer formats. 
However, this is not the main scope of pyDARN and the design pattern shall be decided based on developers of SuperIO/SDARNIO. 

#### Data Visualization (pyDARN)
Data Visualization aspect of pyDARN follows closely to the *matplotlib* library pattern design, **Builder**. 
The goal is to extend *matplotlib's* plotting in pyDARN to include the SuperDARN data visuals and include *matplotlib's* plotting functionality. 
Thus the user should be able to import *matplotlib* and control the figure object as normal to the *matplotlib* API and plot pyDARN plots using the same *matplotlib* object. 

One Caveat to this design pattern is that *matplotlib* actually follows a **singleton** pattern under the hood. So inheritance of *matplotlib* is not an option. 
Also, `Axes` objects need to be passed into all plotting methods to build off that object, following the **builder** pattern due the nature of *matplotlib*. 

Please look at pyDARN's `RTP` class to get a better understand of this design pattern and how to deal with some *matplotlib's* caveats. 

### Standards 
pyDARN follows the following stylistic choices (these can be reviewed at anytime if a strong reasoning of changing is requested):

#### Code

1. Follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) style for python code 
- Replace tabs with 4 spaces
- Develop for python 3.5 and higher, avoid backwards compatibility
- `__init__.py` should be empty except at the base of the library
- Reference any papers/articles/resources regarding algorithms and equations
- If constants are needed define in a shared module and not internally to the code
- reference any documentation explaining SuperDARN formats/data/radar information to avoid future needing to re-update code documentation if things change
- No asserts in code only in testing
- 80 character length lines, but not enforced 
- Use `(` `)` for grouping in python, including imports
- Re-raises should be avoided with respect to PEP 8 style suggestion of minimizing try/except code. If needed it should meet one of the following conditions
  - Re-raising to rename the error the should use `raise from` syntax to include trace-back information.
  - Re-raising is allowed if something needs to happen before an exceptions is raised in that method. 
- Descriptive log and error messages 
- Try to create your own exceptions when raising one instead of pre-built exceptions
- Imports should be alphabetic while still following PEP 8 style 
- Copyright line at the top, see [copyrights and licensing](developer/copyrights_licenses.md)
- Parallization should be the last resort for speeding up code, see [testing](developer/testing_guidelines.md) and [workflow](developer/workflow_guidelines.md)

#### Docstrings

1. Required at the following locations and sections in the code:
    - top of the file: 
        - description of the module (file)
        - Classes/Functions in that file
        - Exceptions raised in that file 
        - Future Work if anything was not addressed 
        - Notes 
    - After class definition:
        - description of the class  
        - Attributes
        - Methods 
    - After method/function definition:
        - Description
        - Parameters
        - Raise: what exceptions are raised in this method
        - Returns: only include if there are returns
        - See Also : what other methods may be of interest to the user (recommended but optional)
        - Notes (optional)
    - Important sections of code that need to be described
    - Test functions: 
        - short summary 
        - expected behaviour: optional
2. Headings follow [Numpy style](https://www.datacamp.com/community/tutorials/docstrings-python#seven-sub) 
3. Short summary: short summaries are a single sentence describing what the function does in a concise way
  - This is included in all descriptions and used for testing functions
4. Extended summary: provides details on what the function does. Should not go into parameter names/details. 
  - This should be separated by a blank line after the short summary 
```python
  def sdarn_read():
  """
  Reads any SuperDARN data file type. 

  The SuperDARN data files types include Iqdat, FitACF, RawACF, Grid, Map. Will read DMap or hdf5 formats 
  of the SuperDARN data file types. 
  """
  pass
```
5. In line comments should follow PEP 8 style and above the line commenting 
6. In line comments should follow the maximum 80 character length

#### Documentation  
1. mkdocs is the used documentation builder 
- Readthedocs is the theme that is used 
- written in markdown
- API style will be decided on a API code generator 
- Use `pydarn.css` for styling tables 
- Copyright documentation, see [copyrights and licensing](developer/copyrights_licensing.md)
- Follow documentation [workflow](developer/workflow_guide.md) 

#### Other Resources 
- More python code style guidelines: [Code Style](https://docs.python-guide.org/writing/style/)
- Install [flake8](http://flake8.pycqa.org/en/latest/) into your text editor 

