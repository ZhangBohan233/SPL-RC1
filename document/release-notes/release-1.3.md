# SPL 1.3 Release

Release date: 2019/03/06
## New Features

#### Syntax changes:
* Removed local-variable keyword `let`

* Keyword `abstract` now works as a quantifier of definition keywords `class` and `function`

* Tags tagged by `@` are implemented:

    `@Override`
    `@Suppress`
    
#### Rework on the function parameter system:
* Default parameter now can contain expressions
* Keyword argument supports
    
#### Functionality augment:
* Functions `print` and `println` are accessible to both stdout and stderr

#### New library class:
* `StringBuilder`
    
#### Optimizations:
* Performance optimization: comparing to SPL 1.2:
    * loops are 22% faster
    * recursions are 45% faster
* Structural reorganization:
    * Deleted spl coder stuff

#### Bugs fixes:
* Fixed some long-existing bugs
