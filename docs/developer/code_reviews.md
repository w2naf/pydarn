<!---
Copyright (C) 2019 SuperDARN Canada, University of Saskatchewan 
Author: Marina Schmidt 
-->
# Code Reviews 

Code Reviews are essential part to software development as it ensure consistency, following of standards, and reduce code defects. Thus code reviews are revered as a strong **best practice** method. They also encourage learning opportunities for those new to the library or the languages. As a goal of pyDARN is to be maintainable and flexible it is requirement that all [Pull Requests](developer/pull_request.md) get a code review. 

However, code reviews can be challenging in delivering in a positive, collaborative and productive environment. Thus here are some guidelines on that are to be followed when giving a code review in *pyDARN*. 

Please note a lot of this content is taken from this code review blog: [The Art of Giving and Receiving Code Reviews](https://www.alexandra-hill.com/2018/06/25/the-art-of-giving-and-receiving-code-reviews/)

[!Code Reviews](imgs/code_quality_3.png)

The goal of code reviews is to encourage good code and avoid discouraging people from developing. 

While commenting on code or replying to feedback remember worth while vs conflict potential:

[!worth vs. conflict](img/graph1.jpg) 

When making comments watch out you don't fall in the left most quadrant as this is seen as pedantry.

## GitHub Code Reviews
GitHub code reviews are rather easy with the web-interface. In the pull request you can start viewing the files that are changed and commenting on them. 
Once you start commenting in the code, a code review will be started. If you close the browser or walk away your comments are not lost so don't feel you need 
to submit every comment made. 
!!! Warning
    Please avoid submitting every comment in a code review, this will cause a lot of notifications to pyDARN followers. 

Once the review is done, you can add summary of general comments you want to see changed or general positives you saw. If changes are needed, please add a check list to the summary so the developer can see what is needed to be done before. 
Before submitting the review you can choose three options to request from the developer: 
- **Comment**: General feedback to the developer and you probably will not re-look over the changes 
- **Approve**: Feedback to the developer and you approve the code to be merged 
- **Request Changes**: Specific feedback that must be addressed before the pull request can be merged
!!! Warning 
    **Request Changes** prevents the pull request from being merged, thus it should only be used when there are changes that need to be made. 

For further instructions on using [GitHub's code review feature](https://help.github.com/en/articles/reviewing-proposed-changes-in-a-pull-request#about-reviewing-pull-requests)


### Request Changes
Because *request changes* prevent pull requests from merging strict rules need to be met so that this power is not abused by reviewers. 
#### Rules 
1. Provide a check list, or list of comments that need to be addressed before a merge
2. Must stay diligent to respond to comments from the developer and changes made to approve requests
3. Changes must fall in *High Reward* section of the above graph and *low Reward* changes should not stop a merge

At the end of the day you must ask yourself **"** *will this code break anything if it is merged* **"** 

!!! Note
    If this feature is abused by the reviewer, they will be warned, then requested to no long code review, then removed from pyDARN collaboration. 
    We need to keep developers encouraged and code moving, this feature can be discouraging when used on pedantic comments and slowing down the process of merging code. 

## For the Developer(s)

### Before the code review 
1. Review your own code, make sure it meets the [code style guide](developer/code_style.md) and [workflow](developer/workflow_guide.md)
2. Make sure you test your own code, don't expect the code reviewer to find bugs in your code
3. Try to keep the number of changed lines to 400, if longer don't expect a fast turn around
4. Be patient, you want the reviewer to take their time 

### After the code review
1. Be mindful of the comments
2. If you do not agree with suggestion/comment, explain your reasoning and opinion 
3. Take discussions offline if you need to


## For the Reviewer(s)

### During the Code Review
1. Keep in mind the [code style guide](developer/code_style.md) is absolute, so avoid pedantic stylistic comments
2. Reserve time for a code review, sometimes you need to look at multiple files or lines to understand a piece of code doing this while trying to focus on another thing might make you assume something or miss something. Remember the developer put time into the code so it is expected you put time into your review.  
3. Look for the following first:
  1. Design - does if follow the desired design of the package 
    - if No, this would be a **request for changes**
  2. Functionality - does it seem user friendly, are there any side behaviours that could occur, does the logic make sense, are there performance hits? 
    - If the package include parallelism look for deadlocks or race conditions
    - If any of these do not meet satisfaction then it is a **request for changes**
  3. Complexity - does it makes sense, is the functionality useful, are they trying to *do it all!* 
    - If Yes, then this may also need a **request for changes** depending how complex the code got
4. If any changes are made that will alter the codes behaviour make sure to remind the developer to write tests for it in a polite manner
5. One the following has been looked at smaller detailed things can be commented on like code style and documentation 
6. Look at over all workflow of the code, if there is a lot to change suggest breaking that pull request into smaller chunks 
7. Review tests last, this way you are more familiar with their code and can see if they are testing all corner cases or not
8. Make sure to review your comments and other reviewers comments to reduce any redundant, pedantic comments 
9. Review [communications guidelines](developer/communications_guidelines.md) to make sure you are supporting a positive collaborative environment focus on:
  - Asking questions instead of pointing out flaws
  - Suggest solutions if there is an issue, like too much complexity
  - Explain why you want a certain change made 
  - Give insight on your knowledge on how to allow the developer to improve
  - focus on the code and not the developer. Avoid personal comments or words like "you"
10. If you need to split the code review into smaller chunks, ask the developer the files to look at first and files to avoid until later
11. If a large portion of the code needs to be revised, don't spend too much time reviewing every line. Ask for them to revise it with more comments, follow code style or break into smaller chunks. 


### After the Code Review 
Generally after a code review the developer will implement your suggestions/comments or pushback. If there is pushback following these guidelines:
1. Try to understand their point of view, remember it is their code 
2. If something needs to be addressed, explain your reasoning and suggestion possible solutions
3. Stay polite
4. Take it offline if the discussion is not moving anywhere 
