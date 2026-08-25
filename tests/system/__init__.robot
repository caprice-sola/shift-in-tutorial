*** Settings ***
Documentation    Directory-level setup: one snip server for every suite in
...              tests/system/, started once and torn down once - not per file.
Library          Process
Library          RequestsLibrary
Suite Setup      Start Snip Server
Suite Teardown   Stop Snip Server

*** Variables ***
${BASE_URL}      http://127.0.0.1:8941
${STARTUP_ATTEMPTS}    20

*** Keywords ***
Start Snip Server
    ${handle}=    Start Process    uvicorn    snip.main:app    --app-dir    src
    ...    --host    127.0.0.1    --port    8941    --log-level    warning
    ...    cwd=${CURDIR}/../..
    Set Suite Variable    ${SERVER_PROCESS}    ${handle}
    Create Session    snip    ${BASE_URL}
    Wait For Server To Be Up

Wait For Server To Be Up
    FOR    ${attempt}    IN RANGE    ${STARTUP_ATTEMPTS}
        ${running}=    Is Process Running    ${SERVER_PROCESS}
        IF    not ${running}
            Fail    uvicorn exited before starting - port ${BASE_URL} may already be in use
        END
        ${up}=    Run Keyword And Return Status    Server Should Respond
        IF    ${up}    RETURN
        Sleep    0.5s
    END
    Fail    snip server didn't come up within ${STARTUP_ATTEMPTS} attempts

Server Should Respond
    ${resp}=    GET On Session    snip    /openapi.json
    Status Should Be    200    ${resp}

Stop Snip Server
    Terminate Process    ${SERVER_PROCESS}
