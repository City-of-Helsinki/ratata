Ratata
======
*Rest API Tuning And Testing Apparatus*

Ratata is a HTTP API tester built with Python 3.

Features
--------
Ratata parses an API-test specification from a YAML-file and runs the tests against a live server.

Given the example:
```YAML
name: Parks API (testing)
address: http://127.0.0.1:10231

requests:
  - name: Your basic index page
    path: "/parks/"
    method: GET  # redundant as GET is default. Can also be PUT or POST or DELETE
    response:
      type: JSON
      code: 200
```

Running this would test that `http://127.0.0.1:10231/parks` accepts a GET request and responds with a 
`Content-type: application/json` header and code `200`.

Dynamic paths <a name="dynamic-paths"></a>
-------------
A Python function returning a string can be used to create dynamic paths. For example:
 
```YAML
[...]
# inside park.yaml
requests:
  - name: Checking for 404
    path: /parks/{% random_park_nonexistent_id %}
    response:
      code: 404
[...]
```

uses a random ID every time the test is run. This function needs to be defined in the supporting module, which is a
Python file in the same directory and with the same name as the specification. The url of the request will be 
given as a parameter. E.g.:

```Python
# inside park.py
import random

def random_park_nonexistent_id(url):
    return random.randint(10, 20)
```

You can also define a top-level `module` attribute to import your supporting code from another location:
```YAML
name: My fancy API
address: http://foo.com
module: my_other_module
```

Request parameters
------------------
Parameters for requests are given in the `params` section:

```YAML
[...]
  - name: The search endpoint uses a GET-parameter
    path: /parks/search
    params:
      t: sunny
      per_page: 10
[...]
```

Parameters can also be dynamic: 

```YAML
[...]
  - name: Create a new park
    path: /parks/
    method: POST
    params:
      name: "{% a_random_park_name %}"
[...]
```
This time `a_random_park_name(url)` function would be run from the supporting module (see [dynamic paths](#dynamic-paths))
and its return value used as the value for `t`. Remember to enclose the name in quotation marks to avoid YAML parsing 
errors.

If you'd like the parameters to be sent as JSON in the request body then use the `format: JSON` definition.
```YAML
[...]
  - name: Create a new park
    path: /parks/
    method: POST
    format: JSON
    params:
      name: "{% a_random_park_name %}"
[...]
```

Response validation
-------------------
The results from requests can be validated in several different ways under the `response` section:
```YAML
  - name: Get information about one specific park
    path: /parks/1
    response:
      type: JSON
      code: 200
      contains: description
      regex: .*description.*  # essentially the same as above, here as an example
      function: validate_random_park
```

Here we make sure the server returns `Content-type: application/json` with code `200` and that the 
returned body contains the text `description` (in two different ways). 

Finally we run the validation function `validate_random_park` giving it the `url` and `result object` as parameters. 
The function should either return `False` or raise `AssertionError` if there is something wrong.
This function should be defined in the supporting module (see [dynamic paths](#dynamic-paths)). Here's an example 
validation function: 

```Python
def validate_random_park(url, response):
    return response.text.find("Porkie Park") != -1  # response is a Requests Response object
```

Define extra headers or cookies
-------------------------------
Just use `headers` or `cookies` inside the request specification:

```YAML
[...]
  - name: Create a new park
    path: /parks/
    method: POST
    headers:
      "X-spiderman": "Is a big one"
      "Content-type": "application/json"
    cookies:
      flavor: "chocolate"
    params:
      name: "{% a_random_park_name %}"
[...]
```

You can also use both on the top-level in which case they'll be applied to every request.

Benchmarking
------------
Use an API-specification to drive performance tests with the `--benchmark` option
```bash
$ python ratata.py --benchmark 12 myspec.yaml
```
This would run every request specification inside `myspec.yaml` 12 times, check results and calculate the 
average response times. All the requests are fired as soon as possible without any throttling.

Only GET-requests will be benchmarked.

Using previous test results
---------------------------
All the test cases are run synchronously and it's possible to use the results of previous cases as input for 
new ones. This in general is bad practise as it makes your tests interdependent and will not work in 
benchmarking where test order is randomized and tests are run asynchronously. However it's sometimes very 
handy, e.g. when creating a resource and later wanting to delete it. Access to previous results happens
through an injected global `RATATA_RESULTS`. Use your request specification `name` as key:

```Python
def previous_park_id(url):
    rs = globals()['RATATA_RESULTS']
    if 'Create a new park' in rs:
        res = rs['Create a new park']
        return res.json()['id']
```


License
-------
MIT