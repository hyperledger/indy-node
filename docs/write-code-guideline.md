# Code quality requirements guideline

Please make sure that you take into account the following items before sending a PR with the new code:

### General items
- Consider sending a design doc into `design` folder (as markdown or PlantUML diagram) for a new feature  before implementing it.
- Make sure that a new feature or fix is covered by tests (try following TDD)
- Make sure that documentation is updated according to your changes (see [docs](.) folder).
In particular, update [transactions](transactions.md) and [requests](requests.md) if you change any transactions or requests format.
- Follow incremental re-factoring approach: 
    - do not hesitate to improve the code
    - put TODO and FIXME comments if you see an issue in the code
    - log tickets in [Indy Jira](https://jira.hyperledger.org/secure/RapidBoard.jspa?rapidView=133&projectKey=INDY&view=planning.nodetail) if you see an issue.

### Code quality items
The current code is not perfect, so feel free to improve it. 
- Follow PEP 8 and keep same code style in all files.
    - Naming. Snake case for functions, camel case for classes, etc.
    - Give names starting with the underscore to class members that are not public by their intention. Don’t use these members outside of the class which they belong to.
    - Docstrings for all public modules and functions/methods. Pay special attention to describing argument list
    - Annotate types for arguments of public functions 
    - Annotate return type for public functions
    - Use flake8 in developer environment and CI (fail a build if the flake8 check does not pass).
    (you can run `flake8 .` on the project root to check it; you can install flake8 from pypi: `pip install flake8`)
- Inheritance and polymorphism
    - Use ABC when creating abstract class to ensure that all its fields implemented in successors.
    - Prefer composition instead of multiple inheritance
    - Avoid creating deep hierarchies
    - Avoid type checks (type(instance) == specific_subclass), we have them in some places and it is awful, do polymorphism instead
    - If there is an interface or abstract class then it should be used everywhere instead of specific instance
    - Make sure that methods of subclass are fully compatible with their declarations in interface/abstract class
- Separation of concerns
    - Follow separation of concerns principles
    - Make components as independent as possible
- Avoid high coupling
    - Some classes have references to each other, for example Node and Replica, so we get a kind of “spaghetti code
- Use classes instead of parallel arrays
- Clear and not duplicated Utilities
- Decomposition
    - There are functions and classes which are too long. For example class Node has more than 2000 lines of code, this complicates understanding of  logic.
    - This can be solved by destructuring of such classes or functions on a smaller one by aggregation, composition and inheritance
- No multiple enclosed if-elif-else statements
    - It’s hard to read the code containing multiple enclosed if-else statements
    - Consider checking some conditions a the beginning of a method and return immediately
- Choose good variable and class names
    - Make variable and name classes to be clear, especially for Public API
    - Avoid unclear abbreviations in public API
- Use asyncio instead of callbacks
    - It  looks and behaves just like a method call - you know that further code is not executed until coroutine completed.
    - It requires no callback preparation - code is cleaner
    - It does not break context - exception raised in a coroutine has the same stack trace as an exception raised in a method (while the one raised in callback don’t)
    - It is easy to chain coroutine calls
    - If it is needed you can easily wrap coroutine in a Future and execute it in non-blocking fashion
- Consider using Actor models (this is our long-term goal for re-factoring to achieve better code quality and performance)     
- Think about performance of the pool


### Test quality items
- Write good tests
    - Not all of our tests are clean and clear enough
    - Follow TDD in writing the tests first
    - Have Unit tests where possible/necessary
    - Avoid using ‘module’ level fixtures if possible
- Use indy-sdk in all tests where possible. 
If it's not possible to use indy-sdk for some reasons 
(for example, indy-sdk doesn't have a required feature), then log a ticket in [Indy-sdk Jira](https://jira.hyperledger.org/secure/RapidBoard.jspa?rapidView=149&projectKey=IS&view=planning.nodetail)
 and put a TODO comment in the test.
- Use `txnPoolNodeSet`, not `nodeSet` fixture. `nodeSet` will be deprecated soon.
- Importing fixtures
    - Fixture imports are not highlighted by IDEs, that’s why they can be accidently removed by someone. To avoid this try to move fixture to conftest of the containing package or conftest of some of higher-level package - this allows fixture to be resolved automatically.
    If you still import fixtures, mark such the imports with the following hint for IDE not to mark them as unused and not to remove them when optimizing imports:
    
        `# noinspection PyUnresolvedReferences`
- Try to use the same config and file folder structure for integration tests as in real environment.
As of now, all tests follow the same file folder structure (see [indy-file-structure-guideline](indy-file-structure-guideline.md))
as Indy-node service, but the folders are created inside `tmp` test folder.
 

 