# Pull Requests and Issues 

pyDARN is hosted on *GitHub* that provides the features of **Issues** and **Pull Requests**. **Issues** are designed for users and developers to report or discuss things in reference to pyDARN. 
General topics for **Issues** are:
- Bugs: an error or incorrect behavior of the code
- Enhancements: an idea of how to improve features/functions
- New Feature: an idea of a new feature/package 
- Documentation: request to update or add something into the documentation 
- Questions: uncertain about a function or want more information on something regarding pyDARN 

**Pull Requests** are designed primarily for developers, and may require users help, to merge code changes into another pyDARN branch, see [workflow guidelines](developer/workflow_guide.md). 
Typical **Pull Requests** pertain to addressing an **Issue** or one of following topics:
- Bug fix: focuses on fixing a bug 
- Enhancement: updating, improving code with an enhancement 
- New feature: adding a new feature
- Deprecation: removing an old feature
- Documentation: updating or adding to current documentation system
- Release: pushing a release version to master 

## Issues
On the [pyDARN GitHub](https://github.com/superdarn/pydarn) page you can create an **Issue** by clicking the *Issues* tab and clicking [*New Issue*](https://github.com/SuperDARN/pydarn/issues/new). 
Because Issues can vary in context there are different standards are set:
### Bugs
1. Title needs to start with "Bug:" or "Error:" with an appropriate title describing the problem
2. Description needs to include:
    - A couple sentence on the bug/problem/error 
    - What was the input you gave the code? Is it a specific file/data set you are using or various files/data sets?
    - Provide the code you used that causes the bug/problem/error
    - Provide the output from the code when it runs (text and/or images) 
    - Provide you expectation of what was supposed to be produced 
    - Any further information you have found
- Assignees is optional if you can think of anyone who would know about this bug the most or people that you may have already talked to about this
- Add bug label and any additional labels pertaining to the bug/problem/error
- Add to the appropriate project, given the urgency of bug it may need to be a *Hotfix* or part of a *Patch* release. 
- Add to the milestones if this in relation to newer code 

### Enhancements
1. Title needs to start with "Enhancement:" or "New Feature:" with an appropriate title describing the enhancement or feature 
2. Description try to include: 
    - A couple sentences on the new enhancement or feature regarding what the purpose of it would be and why it is important
    - If it includes a new function/class please describe how you would see the interface would be. What inputs would it take? Would it return anything, if so what would it return? 
    - If it is a feature from previous work any other details like style of visual or libraries that might be required is also useful 
    - If you have any concerns or want to further discuss post them 
    - Add a check list of things that need to be included/desired/or checked for in the enhancement/feature 
- Add Assignees to the **Issue** if you know their feedback would be good to have or a developer that can help the enhancement or new feature
- Add enhancement or new feature label and any additional labels pertaining to the **Issue**
- Add to the appropriate project if the enhancement is small enough to be part of a *Patch* or big enough to be part of a *Minor* release. New features are big enough for a *Minor* release.
- Add to the milestone if a *Minor* release addition 

## Pull Request 

Pull requests are completed when a completed section of code/functionality/module or simple fix is done on separate branch that is not *develop* or *master*. 
Completed referring to: 
- Tested (see [testing guidelines](developers/testing_guide.md))
- Documented (see [documentation guidelines](developers/documentation_guide.md))

A pull request is [created](https://github.com/SuperDARN/pydarn/pulls) via clicking on **New pull request** and following the guidelines below. 
Once a pull request is created, [travis-CI](https://docs.travis-ci.com/user/tutorial/) will be invoked and will run the following tests:
- macosx, linux, and windows builds for python 3.5+ (Due to python 2.7 being deprecated in 2020, we will not support any python version lower than 3.5)
- testing scripts **yet to be implemented** 
- test coverage **yet to be implemented**
- profiling/benchmarking **future possibility** 
- python style checkers
  - [flake8](http://flake8.pycqa.org/en/latest/): PEP8 style checker for python
  - [MyPy](https://mypy.readthedocs.io/en/latest/introduction.html): python type checker

### Guidelines of Pull Request
The following guidelines are required for the pull request to be approved and the section of code to be accepted.
1. Any non-release branches must be merged into `develop` or another side-branch. Documentation based branches can be merged into `master` if referencing a typo, or further clarification in the current release. [HOT Fixes](developers/release_guidelines.md) still need to be merged to `develop` but will prompt a patch fix release of the current status of `develop`. 
2. Pull request titles: ensure the title of your pull request is **meaningful**. If your pull request is deemed **HOT Fix** worthy from *issue* conversation then put that in the title. 
3. Description: make sure the user understands where this pull request is coming from (i.e., referencing issues or common functionality requests). The current status and any limitations the code does not consider. And how to test your code, give some example code and expected results for the reviewers of your pull request. 
4. Reviewer requesting: at least two reviewers must be requested (of your choice) or a call out to anyone who wants to test your code. One reviewer you pick can be the code reviewer. The code reviewers responsibility is to do a code review on the code (please review [code review guidelines](develoepers/code_reviews.md)). The other reviewer will test your code. However, other reviewers can test/code review the pull request and one reviewer can do both jobs. 
5. No cowboy coding: This means you cannot merge your own pull request. One of the reviewers or members of the pyDARN community can merge your code in. However, it is preferred that one of the reviewers merges it. Pings on the pull request can be made to try and get the attention of the reviewers and others to help speed up a pull request.


