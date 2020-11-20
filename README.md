<p align="center">
    <a href="#"><img src="docs/docs/img/brokermint.png"></a>
</p>
<p align="center">
    <em>Python interface to the Brokermint API</em>
</p>
<p align="center">
    <a href="https://codecov.io/gh/dpguthrie/brokermint" target="_blank">
        <img src="https://img.shields.io/codecov/c/github/dpguthrie/brokermint" alt="Coverage">
    </a>
    <a href="https://pypi.org/project/brokermint" target="_blank">
        <img src="https://badge.fury.io/py/brokermint.svg" alt="Package version">
    </a>
</p>

---

**Documentation**: <a target="_blank" href="https://brokermint.dpguthrie.com">https://brokermint.dpguthrie.com</a>

**Source Code**: <a target="_blank" href="https://github.com/dpguthrie/brokermint">https://github.com/dpguthrie/brokermint</a>

**Brokermint API Documentation**: <a target="_blank" href="https://brokermint.com/api/">https://brokermint.com/api/</a>

---

## Overview

**brokermint** is a python interface to data stored in Brokermint.

The interface allows access to data on Brokermint through the `Client` class:

However, the user **must** supply an `api_key` to access or manipulate any data.  The user can supply the `api_key` when instantiating the `Client` class:

```python
import brokermint as bm

bmc = bm.Client("my_fake_api_key")
```

Or, you can set the environment variable `BM_API_KEY` and call the `Client` class with no arguments:  `bm.Client()`

### Linux / MacOS

```bash
export BM_API_KEY=my_fake_api_key
```

### Windows

```bash
set BM_API_KEY=my_fake_api_key
```

_Note: This environment variable is only available in the current process._

See this link for adding an environment variable that exists outside of this process: https://docs.oracle.com/en/database/oracle/r-enterprise/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html*


## Requirements

Python 3.6+

- [Requests](https://requests.readthedocs.io/en/master/) - The elegant and simple HTTP library for Python, built for human beings.

## Installation

```
pip install brokermint
```

## Example

```python
import brokermint as bm

bmc = bm.Client(api_key="my_fake_api_key")

# Get Transactions - defaults to 1,000
data = bmc.list_transactions()

# Get Transactions, limit to 5
data = bmc.list_transactions(count=5)
```

## License

This project is licensed under the terms of the MIT license.
