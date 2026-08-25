*** Settings ***
Documentation    Cross-cutting flows per docs/test-strategy.md: behaviour
...              that spans the full request pipeline (routing, validation,
...              exception handling) rather than any single unit. Two cases
...              only - this is deliberately thin, not a restatement of the
...              per-case validation table already in tests/unit/test_models.py.
Library          RequestsLibrary
Library          Collections

*** Test Cases ***
Unknown Code Returns Clean 404 Not A Server Error
    ${resp}=    GET On Session    probe    /this-code-does-not-exist
    ...    expected_status=404    allow_redirects=${False}
    Status Should Be    404    ${resp}
    Should Contain    ${resp.json()}[detail]    this-code-does-not-exist

Unsafe Url Is Rejected End To End
    ${body}=    Create Dictionary    url=javascript:alert(1)
    ${resp}=    POST On Session    probe    /api/links    json=${body}
    ...    expected_status=422
    Status Should Be    422    ${resp}
