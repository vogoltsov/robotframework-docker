*** Settings ***
Documentation           DockerComposeLibrary tests.
Library                 DockerComposeLibrary
Library                 Process


*** Test Cases ***
Returns correct Docker Compose version
    ${result} =         Run Process
    ...                 docker  compose  version
    ${found_version} =  Evaluate
    ...                 re.findall(r"(\\d+\\.(?:\\d+\\.)*\\d+)", "${result.stdout}")[0]
    ${library_version} =
    ...                 Docker Compose Version
    Should Be True      "${found_version}" == "${library_version}"
