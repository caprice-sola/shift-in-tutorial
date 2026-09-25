# Robot Framework syntax — the parts that bite

Every example below is taken from a suite in this repository that passes in CI.

## 1. Two or more spaces separate arguments

This is the rule that breaks first-time suites. A keyword and each of its arguments are separated
by **at least two spaces** (we use four). One space makes it part of the keyword name.

```robotframework
Status Should Be    200    ${resp}
```

## 2. A file is divided into sections

```robotframework
*** Settings ***      # imports, documentation, suite setup/teardown
*** Variables ***     # suite-level values
*** Test Cases ***    # the tests
*** Keywords ***      # your own reusable keywords
```

## 3. Variables

| Syntax | Meaning |
|---|---|
| `${name}` | a scalar |
| `@{name}` | a list |
| `&{name}` | a dictionary |
| `${False}`, `${True}`, `${None}` | Python literals |
| `${CURDIR}` | the directory of the current file |

Assignment uses `=` on the left of the keyword call:

```robotframework
${resp}=    GET On Session    snip    /abc
```

## 4. Reaching into a response

`RequestsLibrary` returns the `requests` response object, so Python attribute access works, and
dictionary/index access uses `[...]` **outside** the braces:

```robotframework
${code}=    Set Variable          ${create.json()}[code]
Should Be Equal                   ${follow.headers}[Location]    https://example.com/shift-in
Should Be Equal As Integers       ${stats.json()}[clicks]        3
```

## 5. The RequestsLibrary keywords our suites use

| Keyword | Purpose |
|---|---|
| `Create Session    snip    ${BASE_URL}` | name a base URL once (done in `__init__.robot`) |
| `POST On Session    snip    /api/links    json=${body}` | send JSON |
| `GET On Session    snip    /${code}    expected_status=307    allow_redirects=${False}` | follow a link **without** following the redirect |
| `Status Should Be    201    ${resp}` | assert the status code |

`expected_status=` stops the keyword failing on a non-2xx response — required for 307, 404 and 410.
`allow_redirects=${False}` is what lets you assert on the `Location` header instead of the
redirect target's response.

## 6. Control flow

```robotframework
FOR    ${i}    IN RANGE    3
    ${follow}=    GET On Session    snip    /${code}    expected_status=307
END

IF    not ${running}
    Fail    uvicorn exited before starting
END
```

## 7. Building your own keyword

Anything in `*** Keywords ***` can be called like a built-in. Ours start and stop the server:

```robotframework
*** Keywords ***
Server Should Respond
    ${resp}=    GET On Session    snip    /openapi.json
    Status Should Be    200    ${resp}
```

`Run Keyword And Return Status    Server Should Respond` returns a boolean instead of failing —
useful for polling.

## 8. Running a suite

```bash
robot --outputdir robot-results tests/system/
```

Three artefacts land in `robot-results/`: `report.html` (pass/fail summary), `log.html` (every
keyword, every argument, expand-on-click — read this when something fails) and `output.xml`
(machine-readable, what CI uploads).
