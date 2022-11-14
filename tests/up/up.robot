*** Settings ***
Documentation           DockerComposeLibrary tests.
Library                 DockerComposeLibrary
Library                 Telnet
Test Teardown           Docker Compose Down


*** Test Cases ***
Can Start Services Using Docker Compose
    Docker Compose Up

Can Start Service by Name
    @{service_names} =  Create List
    ...                 httpd
    Docker Compose Up   service_names=${service_names}

Cannot Start Service by Name If It Does Not Exist
    @{service_names} =  Create List
    ...                 unknown
    Run Keyword And Expect Error
    ...                 [[]Docker Compose Up[]] Failed to start services*
    ...                 Docker Compose Up
    ...                 service_names=${service_names}

Can Get Service Host and Port
    Docker Compose Up
    ${service} =        Get Exposed Service  httpd  80
    Should Match Regexp
    ...                 ${service.host}
    ...                 ^\\d{1,3}\\\.\\d{1,3}\\\.\\d{1,3}\\\.\\d{1,3}$
    Should Match Regexp
    ...                 ${service.port}
    ...                 ^\\d{1,5}$

Cannot Get Exposed Service If Port Is Not Exposed
    Docker Compose Up
    Run Keyword And Expect Error
    ...                 [[]Get Exposed Service[]] Port 123 is not exposed for service httpd
    ...                 Get Exposed Service  httpd  123

Cannot Get Exposed Service If Service Does Not Exist
    Docker Compose Up
    Run Keyword And Expect Error
    ...                 [[]Get Exposed Service[]] Failed to query exposed ports for service unknown:*
    ...                 Get Exposed Service  unknown  80

Cannot Get Exposed Service If Service Is Not Started
    Run Keyword And Expect Error
    ...                 [[]Get Exposed Service[]] Failed to query exposed ports for service unknown:*
    ...                 Get Exposed Service  unknown  80

Can Connect to Exposed Service
    Docker Compose Up
    ${service} =        Get Exposed Service  httpd  80
    Open Connection     host=${service.host}  port=${service.port}
    [Teardown]

Cannot Connect to Container Port
    Docker Compose Up
    ${service} =        Get Exposed Service  httpd  80
    Run Keyword And Expect Error
    ...                 *Connection refused*
    ...                 Open Connection     host=${service.host}  port=80
    [Teardown]


Can Get UDP Service Host and Port
    Docker Compose Up
    ${service} =        Get Exposed Service  httpd  514  protocol=udp
    Should Match Regexp
    ...                 ${service.host}
    ...                 ^\\d{1,3}\\\.\\d{1,3}\\\.\\d{1,3}\\\.\\d{1,3}$
    Should Match Regexp
    ...                 ${service.port}
    ...                 ^\\d{1,5}$

Cannot Get Exposed UDP Service With Default Protocol
    Docker Compose Up
    Run Keyword And Expect Error
    ...                 [[]Get Exposed Service[]] Port 514 is not exposed for service httpd
    ...                 Get Exposed Service  httpd  514
