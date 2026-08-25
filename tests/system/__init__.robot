*** Settings ***
Documentation    Directory-level setup: one snip server for every suite in
...              tests/system/, started once and torn down once - not per file.
Library          Process
Library          RequestsLibrary
Suite Setup      Start Snip Server
Suite Teardown   Stop Snip Server

*** Variables ***
${BASE_URL}      http://127.0.0.1:8941

*** Keywords ***
Start Snip Server
    ${handle}=    Start Process    uvicorn    snip.main:app    --app-dir    src
    ...    --host    127.0.0.1    --port    8941    --log-level    warning
    ...    cwd=${CURDIR}/../..
    Set Suite Variable    ${SERVER_PROCESS}    ${handle}
    Wait Until Keyword Succeeds    20x    0.5s    Server Should Be Up

Server Should Be Up
    Create Session    probe    ${BASE_URL}
    ${resp}=    GET On Session    probe    /openapi.json
    Status Should Be    200    ${resp}

Stop Snip Server
    Terminate Process    ${SERVER_PROCESS}
