# Release Guidelines 

pyDARN is a volunteer community effort thus the release of the software will occur based on cumulative efforts and will avoid timelines. 

!!! Note
    This guideline will be reviewed yearly to ensure the current release guidelines are followed. Otherwise a discussion on a new release system will be discussed. 

## Workflow 

Release will be proposed through **GitHubs** [projects](https://github.com/features/project-management/) by dividing the bare minimum to make the various types of releases: 
- Major: structural, user interfacing changes
- Minor: new or deprecated features and bug fixes 
- Patch: bug fixes 
- Hotfix: major bug fix 

!!! Note
    Hotfix will be pushed directly into master with a patch version number change.

Less types of releases can be included into the larger milestones if completed roughly at the same time. The release workflow will be as follows for Major and Minor releases:
1. Create release branch 
2. Release/announce the beta version to community
3. Once enough user/developers approve on the changes 
4. Create release candidate branch to do any final clean up and getting documentation ready for the new release
5. Build release artifacts   
    - [ ] Change version in `setup.py`
    - [ ] Merge code to master branch
    - [ ] Tag the release version on [GitHub](https://help.github.com/en/github/administering-a-repository/creating-releases)
    - [ ] DOI with [zenodo](https://zenodo.org/)
    - [ ] Upload to [PyPI](https://pypi.org/) 
    - [ ] Update Wiki/README on release history  
6. Upload release artifacts 
7. Notify the community 
  - Email the SuperDARN Users emailing group 

At least one week should be given between each week to allow users and developers to do an testing or fixes to the code. 
For Patches steps 1, 3, and 5 will be taken and for Hotfixes the branch will be merged directly to master and addition changes to push will be need if desired. 

During a release, continuous development can happen on the develop branch to ensure any other pull requests or issues get attention.

The nomenclature for releases are: <Major number>.<Minor number>.<Patch><b-beta or rc for release candidate>. When the branch is created it will have the name of `release/<major>.<minor>.<path><b or rc>`. 
