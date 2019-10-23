# Workflow 

In pyDARN, all additive code whether it is a *bug fix* or *enhancement* must flow the general workflow and merged via a **pull request**.
Special workflows include: 
  - HotFixes 
  - Release 
Please see [release guidelines](developer/release_guide.md) to get more information on these two special cases. 

## General workflow
General workflow will follow the following steps:
1. Create an **Issue** if necessary. New features already planned out or quick bug fixes don't always need an **Issue**
2. 
- Create a branch for your code changes following the branch naming convention mentioned below
- Ensure your code meets the following guidelines:
    - [code style](developer/code_style.md)
    - [testing](developer/testing_guide.md)
- Create a **Pull Request** merging either into a *parent branch* or *develop*
- Add your 
- Follow [pull request](developer/pull_request_issues.md) and [code review](code_review_guidelines.md) guidelines
- Merge **pull request** 

### Branch Workflow
Depending on the purpose of the code the nomenclature and workflow of the branching will change, however, every branch has to at least include the module name in it. 
Avoid using special characters except underscores to keep things consistent. 
Types of branches and their nomenclature:
- **Bug fix**: `<module>/<problem>_fix`. 
    Example: `RTP/overlapping_fix`, `superdarn/RAWACF_Format_fix`
- **HotFix**: `<module>/<problem>_HOTFIX`
    Example: `RTP/time_series_HOTFIX`
- **Enhancement**: `<module>/<enhancement name>` or `<module>/<enhancement>_update`
    Example: `Dmap/seek_method`
- **Deprecation**: `<package or module>/<what is being deprecated>_Deprecated`
    Example: `IO/dmap_Deprecated`, `Dmap/test_integrity_Deprecated`
- **Feature** depending on the new feature if it is only a new method/function then: `<module>/<feature name>` or `<module>/<feature name>_new` 
    Example: `utils/dmap2dict_new`, the new option is if you want to separate it from a enhancement. Please see Feature workflow below for more details on new modules or packages. 
- **Documentation**: `doc/<documentation being updated>`
    Example: `doc/dmap_tutorial`, `doc/borealis_typo`

!!! Note: 
    Module is the file name your code changes are in and package is the folder the code files reside in. If your code changes are in more than one file, you can also use the package name. 

### Feature Workflow
Features can be larger than simple new methods/functions where enhancements are confined to updated code or new methods/functions that can enhance the class functionality. 
Features are a new building block to the library and may require multiple branches. The general feature workflow should follow these steps:
1. Determine the main scope of your new feature this will contribute to your *parent branch* 
    - Nomenclature for a *parent branch*: `<feature or package name>`, if it is a new module then `<package>/new_<module>`
2. Divide that scope up into smaller chunks, this may follow modules, classes, or main methods. This breakdown will contribute to *children branches*.
    - Nomenclature for *child branch*: `<feature or new name module>/<sub task, class, module, method/function>` 
3. If the child scope is too big still divide it up again following step 2. 
4. If any enhancements comes from the above branches, break off accordingly and name based on enhancement nomenclature. 

Each *child branch* will get its own **pull request** into the *parent branch* this ensures smaller scope for code reviews and continuous development on a feature.
Once all *child branches* are merged into the *parent branch* and the *parent branch* is retested then the developer can create a **pull request** to be merged into `develop`.

### Pull Request Workflow
Once code changes are made, tested and checked it follows the code style for pyDARN then a **pull request** can be made. If none of those conditions are met then the **pull request** will be closed until the developer meets the condition. This is to ensure minimal time during code reviews and testing and avoid spamming of commit messages on the **pull request**. 

As mentioned in the branch workflow section all branches except *child branches*, **HOTFIXES**, *release*, and some *documentation* branches are merged to `develop`. For the exceptions:
- *child branch* --> *parent branch*
- **HOTFIXES** --> `master`
- *release* --> `master`
- *documentation* --> `master` if updating the release documentation, newer documentation updates go to `develop`

See [Pull Requests](developer/pull_request_issues_guide.md) for more details on creating a pull request and guidelines to follow. 

Then the workflow should be as follows:
1. Request reviewers and testers 
-  Change/review any comments or bugs in the code reviewers find. See [code review guidelines](developer/code_review_guide.md) for more information on code reviews. 
- Then one of the community members can merge the **pull request** 

## Special Workflows 
Similar to the general workflow *release* and *HotFixes* have slightly different workflows. 
### Release 
1. Create a project on GitHub for the type of release. See [release guidelines](develop/release_guide.md)
2. Once the project to do list is complete create a branch from `develop` for the beta release
3. Then repeat setp 2 for release candidate if necessary 
4. Following the setps in [release guidelines](develop/release_guide,md) to merging the release branch into `master`

### HOTFIX 
Hotfixes are a special type of branch where there is a **major** but in the current release that needs to be fixed. These merges do not always require a version number change but if it does it will be considered a *path* number. The workflow will be as follow:
1. Create **HOTFIX** branch based on the bug 
2. Test the branch then merge to `master`
3. Update any documentation or release artifacts if major enough

### Documentation Workflow
Documentation can always be improved with better example, more concise explanations and new guidelines. When creating a **pull request** the branch can be merged in `master` or `develop` depending what was changes. If the documentation on touches on current release information and will be improving it then it can be merged to `master`. However, if it contains any thing new to the current release or will be enforced in the next release for guidelines then it should be merged to `develop`. 
