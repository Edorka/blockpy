# BlockPy

[![Build Status](https://travis-ci.org/Edorka/blockpy.svg?branch=master)](https://travis-ci.org/Edorka/blockpy)

Minimal python implementation of a blockchain. Following the article [A blockchain in 200 lines of code](https://medium.com/@lhartikk/a-blockchain-in-200-lines-of-code-963cc1cc0e54).

# Running the tests

If you don't trust the green tag from travis-ci.org you can run tests on your own:

```
virtualenv -p python3 venv
source venv/bin/activate
python -m unittest discover tests
```

**Get Blocks**
----
  Returns a list of the chain blocks in JSON format.

* **URL**

  /blocks

* **Method:**

  `GET`
  
*  **URL Params**

   **Optional:**
 
   `from_index=[integer]`

* **Data Params**

  None

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{ items: [{ index: <index>, timestamp: <float>, "data": <Object>, hash: <Hex digest of SHA256 for current object>}] }`
 
* **Error Response:**

  * **Code:** 500 ERROR <br />
    **Content:** `{ error : <error message> }`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/blocks/?from_index=5",
      dataType: "json",
      type : "GET",
      success : function(r) {
        console.log(r);
      }
    });
  ```
