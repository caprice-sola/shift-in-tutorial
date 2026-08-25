*** Settings ***
Documentation    Full-process black-box check on the redirect hot path
...              (create -> follow -> stats), covering SLIs 2 (availability), 3 (resolve
...              correctness), and 5 (stats accuracy) per docs/test-strategy.md. NOT SLI 1
...              (latency) - that's measured, with an actual assertion, by tests/gates/.
...              Not a restatement of the unit suite - this is the one thing only a real
...              running server can prove: the whole stack wired together correctly.
Library          RequestsLibrary
Library          Collections

*** Test Cases ***
Create Follow And Check Stats Round Trip
    ${body}=    Create Dictionary    url=https://example.com/shift-in
    ${create}=    POST On Session    snip    /api/links    json=${body}
    Status Should Be    201    ${create}
    ${code}=    Set Variable    ${create.json()}[code]
    Should Be Equal    ${create.json()}[url]    https://example.com/shift-in
    Should Be Equal As Integers    ${create.json()}[clicks]    0

    FOR    ${i}    IN RANGE    3
        ${follow}=    GET On Session    snip    /${code}
        ...    expected_status=307    allow_redirects=${False}
        Status Should Be    307    ${follow}
        Should Be Equal    ${follow.headers}[Location]    https://example.com/shift-in
    END

    ${stats}=    GET On Session    snip    /api/links/${code}/stats
    Status Should Be    200    ${stats}
    Should Be Equal As Integers    ${stats.json()}[clicks]    3
