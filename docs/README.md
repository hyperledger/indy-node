# Documentation README
Check out the docs at http://hyperledger-indy.readthedocs.io/projects/node

Learn more about how our docs are built and maintained at http://hyperledger-indy.readthedocs.io/en/latest/docs.html

This `docs/` directory should contain all of the documents associated with the repository, with the exception of README files that describe technical details with the directories of code. 

The `docs/source/` directory contains all of the documentation that is built and hosted on readthedocs. Based on the maintainer's discretion, some docs may not be necessary to build on readthedocs, and can exist within the `docs/` directory but outside of the `source/` directory. 


## How to Add Documentation
For new features and pull requests, maintainers should make sure that the **contributor has added an explanation for their changes in the docs folder before merging the PR.**
  
Contributors should add a new file to the docs/source/ folder or write an addition to a current file that explains what their feature is and how it works. If needed, they may also add a link to more technical README's located nearer to the code.

Whenever additions are made to the docs, make sure to update the `index.rst` in whichever folder the file has been added, and build the docs locally to confirm they work (TODO: add the `sphinx-build` command to our CI/CD flow).

For example, if I wanted to add another file to the indy-sdk docs/ folder named `glossary.md`, I would create the file, and then add a reference to it in the `index.rst`: 
```
.. toctree::
  :maxdepth: 1
  :hidden:

  getting-started/index.rst
  ...
  key-concepts.md
  ...
  contributing/index.rst
  ...
  glossary.md                   .. <-- this is your new file!

```

To add a new file to a subfolder, simply update the subfolder's `index.rst` with the relative link to your file.

If you'd like to link to a file outside of the docs/ folder, you'll need to provide an external github link (this is by design, to keep our docs organized into a single folder)

## Building the docs on your machine

Here are the quick steps to achieve this on a local machine without depending on ReadTheDocs. Note: Instructions may differ depending on your OS.
Run these commands within the repository folder
```bash
cd docs/source # Be in this directory. Makefile sits there.
pip install -r requirements.txt
make html
```

This will generate all the html files in `docs/source/_build/html` which you can then browse locally in your browser. Every time you make a change to the documentation you will need to rerun `make html`.

## Additional Instructions
This section is to be used for repo maintainers to add additional documentation guidelines or instructions. 
**TODO: Build the respective code API's into the readthedocs website**

**TODO: Add table support for markdown files** 
* This link may help: https://github.com/ryanfox/sphinx-markdown-tables