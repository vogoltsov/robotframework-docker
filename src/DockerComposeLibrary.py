# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""Robot Framework Docker Library."""

import os
import re
import subprocess
import sys
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
            self._project_name = re.sub(r'\W', '_', BuiltIn().get_variable_value('${SUITE NAME}'), re.ASCII).lower()

        if project_directory is not None:
            self._project_directory = project_directory
        else:
            self._project_directory = os.path.dirname(self._file)

        logger.info(f'Docker Compose project "{self._project_name}" initialized using configuration file: {self._file}')

    # pylint: disable=R0912, R0913, C0103
    def docker_compose_pull(self,
                            no_parallel: bool = False,
                            include_deps: bool = False,
                            service_names: List[str] = None) -> None:
        """Pulls images for services defined in a Compose file, but does not start the containers.
        All parameters are forwarded to `docker-compose`.

        `no_parallel` Disable parallel pulling (default: False).

        `include_deps` Also pull services declared as dependencies (default: False).

        `service_names` A list of service names to be pulled.


        = Examples =

        Pull All Service Images
        | Docker Compose Pull |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('pull')
        cmd.append('--quiet')

        if no_parallel:
            cmd.append('--no-parallel')

        if include_deps:
            cmd.append('--include-deps')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'Failed to pull image(s): {e.output.rstrip()}') from e

    # pylint: disable=R0912, R0913, C0103
    def docker_compose_build(self,
                             compress: bool = False,
                             force_rm: bool = False,
                             no_cache: bool = False,
                             no_rm: bool = False,
                             parallel: bool = False,
                             pull: bool = False,
                             build_args: dict = None,
                             service_names: List[str] = None) -> None:
        """Build or rebuild services.
        All parameters are forwarded to `docker-compose`.

        `compress` Compress the build context using gzip (default: False).

        `force_rm` Always remove intermediate containers (default: False).

        `no_cache` Do not use cache when building the image (default: False).

        `no_rm` Do not intermediate containers after a successful build (default: False).

        `parallel` Build images in parallel (default: False).

        `pull` Always attempt to pull a newer version of the image (default: False).

        `service_names` A list of service names to be built.
        All services are started by default.


        = Examples =

        Build Images
        | Docker Compose Build |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('build')
        cmd.append('--quiet')

        if compress:
            cmd.append('--compress')

        if force_rm:
            cmd.append('--force-rm')

        if no_cache:
            cmd.append('--no-cache')

        if no_rm:
            cmd.append('--no-rm')

        if parallel:
            cmd.append('--parallel')

        if pull:
            cmd.append('--pull')

        if build_args is not None:
            for key, value in build_args.items():
                cmd.append('--build-arg')
                cmd.append(f'{key}={value}')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'Failed to build image(s): {e.output.rstrip()}') from e

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
                        f' is not supported for docker-compose version {self._docker_compose_version}')

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
                        f' is not supported for docker-compose version {self._docker_compose_version}')

        if remove_orphans:
            cmd.append('--remove-orphans')

        if service_names is not None:
            cmd.extend(service_names)

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'Failed to start services: {e.output.rstrip()}') from e

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
                        f' is not supported for docker-compose version {self._docker_compose_version}')

        if rmi is not None:
            cmd.append('--rmi')
            cmd.append(rmi)

        if volumes:
            cmd.append('--volumes')

        if remove_orphans:
            cmd.append('--remove-orphans')

        try:
            subprocess.check_output(cmd,
                                    cwd=self._project_directory,
                                    stdin=subprocess.DEVNULL,
                                    stderr=subprocess.STDOUT,
                                    encoding=sys.getdefaultencoding(),
                                    text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'Failed to shutdown services: {e.output.rstrip()}') from e

    def docker_compose_logs(self,
                            write_to: str = None,
                            prefix: bool = True,
                            timestamps: bool = True,
                            service_names: List[str] = None) -> None:
        """Grabs or saves the output from containers.

        `write_to` Name of the log file to use. Can be an absolute or
        relative path. Relative paths are looked up relative to the
        working directory of the Robot Framework process, not relative
        to the Docker Compose project. If not specified, the logs are
        captured and returned from the keyword.

        `prefix`: If false, `--no-log-prefix` is passed to `docker-compose`
        (default: True).

        `timestamps`: If true, `--timestamps` is passed to `docker-compose`
        (default: True).

        `service_names` A list of service names to limit which logs are gotten.

        = Examples =

        Save container logs to a file
        | Docker Compose Logs | write_to=/tmp/containers.log |

        Grab container logs into a variable
        | ${logs} = | Docker Compose Logs |
        """

        cmd: [str] = self._prepare_base_cmd()
        cmd.append('logs')
        cmd.append('--no-color')

        if not prefix:
            cmd.append('--no-log-prefix')

        if timestamps:
            cmd.append('--timestamps')

        if service_names is not None:
            cmd.extend(service_names)

        if write_to is not None:
            # pylint: disable=consider-using-with
            output_file = open(write_to, 'a', encoding=sys.getdefaultencoding())
            close_output_file = output_file.close
        else:
            output_file = subprocess.PIPE
            close_output_file = DockerComposeLibrary._do_nothing

        try:
            process = subprocess.run(cmd,
                                     check=True,
                                     cwd=self._project_directory,
                                     stdin=subprocess.DEVNULL,
                                     stdout=output_file,
                                     stderr=subprocess.PIPE,
                                     encoding=sys.getdefaultencoding(),
                                     text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(f'Failed to get logs: {e.stderr}') from e
        finally:
            close_output_file()

        if write_to is None:
            return process.stdout
        return None

    def get_exposed_service(self,
                            service_name: str,
                            port: int,
                            protocol: str = None):
        """Retrieves host address and port number for a port exposed by service.

        `service_name` Service name from Compose file.

        `port` Exposed service port number.


        = Examples =

        Get Httpd Exposed Service
        | ${service} = | Get Compose Exposed Service | httpd | 80 |
        | Log To Console | Services is located at ${service.host}:${service.port} |
        """

        info = self._get_exposed_port(service_name, port, protocol)
        service = ExposedServiceInfo()
        if self._is_inside_container():
            service.host = self._get_container_gateway_ip()
        elif info[0] == '0.0.0.0':
            service.host = '127.0.0.1'
        else:
            service.host = info[0]
        service.port = info[1]
        return service

    def _get_exposed_port(self, service_name: str, port: int, protocol: str) -> [str]:
        """Helper function to retrieve info about exposed port by calling 'docker-compose port'."""
        cmd = self._prepare_base_cmd()
        cmd.append('port')
        if protocol is not None:
            cmd.append('--protocol')
            cmd.append(protocol)
        cmd.append(service_name)
        cmd.append(str(port))

        try:
            output = subprocess.check_output(cmd,
                                             cwd=self._project_directory,
                                             stdin=subprocess.DEVNULL,
                                             stderr=subprocess.STDOUT,
                                             encoding=sys.getdefaultencoding(),
                                             text=True)
        except subprocess.CalledProcessError as e:
            raise AssertionError(e.output.rstrip()) from e
        result = output.rstrip().split(':')
        if len(result) == 1:
            raise AssertionError(f'Port {port} is not exposed for service {service_name}')
        return result

    def _prepare_base_cmd(self) -> [str]:
        """Helper function to create a 'docker-compose' command with project name and file arguments."""
        return [
            'docker-compose',
            '--project-name', self._project_name,
            '--file', self._file,
        ]

    def _get_docker_compose_version(self) -> packaging.version.Version:
        """Helper function to retrieve docker-compose version"""
        try:
            cmd = [
                'docker-compose',
                '--version',
            ]
            version_string = subprocess.check_output(cmd,
                                                     cwd=self._project_directory,
                                                     stdin=subprocess.DEVNULL,
                                                     stderr=subprocess.STDOUT,
                                                     encoding=sys.getdefaultencoding(),
                                                     text=True).rstrip()
            version_string = re.findall(r'(?:(\d+\.(?:\d+\.)*\d+))', version_string)[0]
            return packaging.version.parse(version_string)
        except Exception as e:
            raise AssertionError('Could not determine docker-compose version') from e

    @staticmethod
    def _is_inside_container() -> bool:
        """Helper function to check whether the test is running inside a Docker container."""
        return os.path.exists('/.dockerenv')

    def _get_container_gateway_ip(self) -> str:
        """Helper function to retrieve current Docker container gateway ip address."""
        cmd = [
            'docker',
            'inspect',
            '-f',
            '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}',
            DockerComposeLibrary._get_container_id()
        ]
        output = subprocess.check_output(cmd,
                                         cwd=self._project_directory,
                                         stdin=subprocess.DEVNULL,
                                         stderr=subprocess.STDOUT,
                                         encoding=sys.getdefaultencoding(),
                                         text=True)
        return output.rstrip()

    @staticmethod
    def _get_container_id() -> str:
        """Helper function to retrieve current Docker container id."""
        with open('/proc/self/mountinfo', 'r', encoding=sys.getdefaultencoding()) as file:
            for line in iter(file.readline, b''):
                if '/docker/containers/' not in line:
                    continue
                return line.split('/docker/containers/')[-1].split('/')[0]
            raise AssertionError('Failed to obtain container id')

    @staticmethod
    def _do_nothing(*args):
        pass
