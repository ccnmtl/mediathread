# Contributing to Mediathread

We'd love for you to contribute to our source code and to make Mediathread even better than it is
today! Here are the guidelines we'd like you to follow:

 - [Code of Conduct](#coc)
 - [Question or Problem?](#question)
 - [Issues and Bugs](#issue)
 - [Getting Started](#start)
 - [Coding Rules](#rules)
 - [Making Trivial Changes](#trivial)
 - [Making Changes](#changes)
 - [Submitting Changes](#submit)
 - [Further Info](#info)

## <a name="coc"></a> Code of Conduct
Help us keep Mediathread open and inclusive. Please read and follow our [Code of Conduct](https://github.com/ccnmtl/mediathread/blob/master/CODE_OF_CONDUCT.md).

## <a name="question"></a> Got a Question or Problem?

If you have questions about how to use Mediathread, please direct these to the [Google Group](https://groups.google.com/forum/#!forum/mediathread).

## <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
submitting an issue to our [GitHub issue tracker](https://github.com/ccnmtl/mediathread/issues). Even better you can submit a Pull Request with a fix :heart_eyes:.

**Please see the Submission Guidelines below**.

## <a name="start"></a> Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free)
* Submit a ticket for your issue, assuming one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Fork the repository into your account on GitHub

## <a name="rules"></a> Coding Rules
To ensure consistency throughout the source code, please keep these rules in mind as you are working:

* All features or bug fixes **must be tested** by one or more unit tests.
* We follow the conventions contained in:
     * Python's [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/) (enforced by [flake8](https://pypi.python.org/pypi/flake8))
     * Javascript's [ESLint](https://eslint.org/) errors and warnings.
* The master branch is continuously integrated by [Travis-CI](https://travis-ci.org/ccnmtl/mediathread), and all tests must pass before merging.

## <a name="trivial"></a>Making Trivial Changes

### Documentation

For changes of a trivial nature to comments and documentation, it is not
always necessary to create a new github issue or sign a contributor agreement.

## <a name="changes"></a>Making Changes

* Create a topic branch from where you want to base your work.
  * This is usually the master branch.
  * Only target release branches if you are certain your fix must be on that
    branch.
  * To quickly create a topic branch based on master; `git checkout -b
    fix/master/my_contribution master`. Please avoid working directly on the
    `master` branch.
* Create your patch, **including appropriate test cases**.
* Make commits of logical units.
* Run `make jenkins` to make sure the code passes all validation, flake8, eslint and unit tests
* Make sure your commit messages are in the proper format.

## <a name="submit"></a>Submitting Changes
* Push your changes to a topic branch in your fork of the repository.
* Submit a pull request to the repository in the ccnmtl organization.
* The core team reviews Pull Requests on a regular basis, and will provide feedback

## <a name="info"></a> Further Information
For more information, see:
* [Mediathread's Web Site](https://mediathread.ctl.columbia.edu)
* [GitHub Wiki](https://github.com/ccnmtl/mediathread/wiki)
* [Knowledge Base](https://mediathread.ctl.columbia.edu/kb/)
