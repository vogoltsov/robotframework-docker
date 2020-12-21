# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""Robot Framework Docker Library."""

import os
import re
import subprocess
from typing import List

import packaging.version
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.DateTime import convert_time


# pylint: disable=R0903
class ExposedServiceInfo:
    """Defines info for specific exposed service port."""
    host: str
    port: str


class DockerComposeLibrary:
    """DockerComposeLibrary is a part of Robot Framework Docker Library
    that is used for running multi-container Docker applications using 'docker-compose'.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    _docker_compose_version: packaging.version.Version
    _file: str = None
    _project_name: str = None
    _project_directory: str = None

    def __init__(self,
                 file=None,
                 project_name=None,
                 project_directory=None):
        """Initializes an instance of DockerComposeLibrary to use a given Compose file and project name.

        `file` Path to compose file. By default, tries to use 'docker-compose.yml'
        in a directory where current test suite source file is located.

        `project_name` Specify an alternate project name (default: test suite name).
        """
        self._docker_compose_version = self._get_docker_compose_version()

        if file is not None:
            self._file = file
        else:
            suite_source = BuiltIn().get_variable_value('${SUITE SOURCE}')
            suite_directory = os.path.dirname(suite_source)
            self._file = os.path.join(suite_directory, 'docker-compose.yml')

        if project_name is not None:
            self._project_name = project_name
        else:
            self._project_name = BuiltIn().get_variable_value('${SUITE NAME}')

        if project_directory is not None:
            self._project_directory = project_directory
        else:
            self._project_directory = os.path.dirname(self._file)

        logger.info('Docker Compose project "{}" initialized using configuration file: {}'
                    .format(self._project_name, self._file))

    # pylint: disable=R0912, R0913, C0103
    def docker_compose_up(self,
                          timeout: str = '10 seconds',
                          no_deps: bool = False,
                          force_recreate: bool = True,
                          always_recreate_deps: bool = None,
                          no_recreate: bool = False,
                          no_build: bool = False,
                          no_start: bool = False,
                          build: bool = False,
                          renew_anon_volumes: bool = True,
                          remove_orphans: bool = True,
                          service_names: List[str] = None) -> None:
        """Builds, (re)creates, starts, and attaches to containers for a service.
        All parameters are forwarded to `docker-compose`.

        `no_deps` Don't start linked services (default: False).

        `force_recreate` Recreate containers even if their configuration
        and images haven't changed (default: False).

        `always_recreate_deps` Recreate dependent containers (default: False).
        Incompatible with 'no_recreate`.

        `no_recreate` If containers already exist, don't recreate

        `no_build` Don't build an image, even if it's missing (default: False).

        `no_start` Don't start the services after creating them (default: False).

        `build` Build images before starting containers (default: False).

        `renew_anon_volumes` Recreate anonymous volumes instead of retrieving data
        from the previous containers (default: True).

        `remove_orphans` Remove containers for services not defined
        in the Compose file (default: True).

        `service_names` A list of service names to be started.
        All services are started by default.


        = Examples =

        Start All Services
        | Docker Compose Up |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('up')
        cmd.append('--timeout')
        cmd.append(str(int(convert_time(timeout))))
        cmd.append('-d')

        if no_deps:
            cmd.append('--no-deps')

        if force_recreate:
            cmd.append('--force-recreate')

        if self._docker_compose_version >= packaging.version.parse('1.19.0'):
            if always_recreate_deps is None or always_recreate_deps is True:
                cmd.append('--always-recreate-deps')
        elif always_recreate_deps is not None:
            logger.warn('Docker Compose Up: --always-recreate-deps option'
                        ' is not supported for docker-compose version {}'
                        .format(self._docker_compose_version))

        if no_recreate:
            cmd.append('--no-recreate')

        if no_build:
            cmd.append('--no-build')

        if no_start:
            cmd.append('--no-start')

        if build:
            cmd.append('--build')

        if self._docker_compose_version >= packaging.version.parse('1.19.0'):
            if renew_anon_volumes is None or renew_anon_volumes is True:
                cmd.append('--renew-anon-volumes')
        elif always_recreate_deps is not None:
            logger.warn('Docker Compose Up: --renew-anon-volumes option'
                        ' is not supported for docker-compose version {}'
                        .format(self._docker_compose_version))

        if remove_orphans:
            cmd.append('--remove-orphans')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd, cwd=self._project_directory, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise AssertionError('Failed to start services: {}'
                                 .format(e.output.decode('utf-8').rstrip())) from e

    def docker_compose_down(self,
                            timeout: str = None,
                            rmi: str = None,
                            volumes: bool = True,
                            remove_orphans: bool = True) -> None:
        """ Stops and removes containers, networks, volumes and images created by 'up'.
        All parameters are forwarded to `docker-compose`.

        As this function is intended to be used in teardown,
        to help keep the test environment clean,
        the following parameters are added to `docker-compose down` by default:
        - --remove-orphans
        - --volumes

        `timeout` Specify shutdown timeout in seconds (default: 10).

        `rmi` Remove images. Specify 'all' ro remove all images used by any service
        or 'local' to remove only images that don't have a custom tag set by the 'image' field.

        `volumes` Remove named volumes declared in the 'volumes' section of the Compose file
        and anonymous volumes attached to containers.

        `remove_orphans` Remove containers for services not defined in the Compose file.


        = Examples =

        Stop And Remove All Containers And Volumes
        | Docker Compose Down |

        Stop And Remove All Containers And Volumes
        | Docker Compose Down |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('down')

        if self._docker_compose_version >= packaging.version.parse('1.18.0'):
            if timeout is None:
                timeout = '10 seconds'
            cmd.append('--timeout')
            cmd.append(str(int(convert_time(timeout))))
        elif timeout is not None:
            logger.warn('Docker Compose Down: --timeout option'
                        ' is not supported for docker-compose version {}'
                        .format(self._docker_compose_version))

        if rmi is not None:
            cmd.append('--rmi')
            cmd.append(rmi)

        if volumes:
            cmd.append('--volumes')

        if remove_orphans:
            cmd.append('--remove-orphans')

        try:
            subprocess.check_output(cmd, cwd=self._project_directory, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise AssertionError('Failed to shutdown services: {}'
                                 .format(e.output.decode('utf-8').rstrip())) from e

    def get_exposed_service(self,
                            service_name: str,
                            port: int):
        """Retrieves host address and port number for a port exposed by service.

        `service_name` Service name from Compose file.

        `port` Exposed service port number.


        = Examples =

        Get Httpd Exposed Service
        | ${service} = | Get Compose Exposed Service | httpd | 80 |
        | Log To Console | Services is located at ${service.host}:${service.port} |
        """

        info = self._get_exposed_port(service_name, port)
        service = ExposedServiceInfo()
        service.host = info[0] if not self._is_inside_container() else self._get_container_gateway_ip()
        service.port = info[1]
        return service

    def _get_exposed_port(self, service_name: str, port: int) -> [str]:
        """Helper function to retrieve info about exposed port by calling 'docker-compose port'."""
        cmd = self._prepare_base_cmd()
        cmd.append('port')
        cmd.append(service_name)
        cmd.append(str(port))
        try:
            output = subprocess.check_output(cmd, cwd=self._project_directory, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise AssertionError(e.output.decode('utf-8').rstrip()) from e
        result = output.decode('utf-8').rstrip().split(':')
        if len(result) == 1:
            raise AssertionError('Port {} is not exposed for service {}'.format(port, service_name))
        return result

    def _prepare_base_cmd(self) -> [str]:
        """Helper function to create a 'docker-compose' command with project name and file arguments."""
        return [
            'docker-compose',
            '--project-name', self._project_name,
            '--file', self._file,
        ]

    @staticmethod
    def _get_docker_compose_version() -> packaging.version.Version:
        """Helper function to retrieve docker-compose version"""
        try:
            version_string = subprocess.check_output([
                'docker-compose',
                '--version',
            ]).decode('utf-8').rstrip()
            version_string = re.findall(r'(?:(\d+\.(?:\d+\.)*\d+))', version_string)[0]
            return packaging.version.parse(version_string)
        except Exception as e:
            raise AssertionError('Could not determine docker-compose version') from e

    @staticmethod
    def _is_inside_container() -> bool:
        """Helper function to check whether the test is running inside a Docker container."""
        return os.path.exists('/.dockerenv')

    @staticmethod
    def _get_container_gateway_ip() -> str:
        """Helper function to retrieve current Docker container gateway ip address."""
        return subprocess.check_output([
            'docker',
            'inspect',
            '-f',
            '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}',
            DockerComposeLibrary._get_container_id()
        ]).decode('utf-8').rstrip()

    @staticmethod
    def _get_container_id() -> str:
        """Helper function to retrieve current Docker container id."""
        with open('/proc/1/cpuset', 'r') as file:
            return file.read().rstrip().split('/')[2]
