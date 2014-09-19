""" Support functions for jenkinsapi django compatibility """

import jenkinsapi
from jenkinsapi.job import Job
from jenkinsapi.invocation import Invocation
from jenkinsapi.custom_exceptions import WillNotBuild, UnknownJob
import jenkinsapi.job
import requests

from time import sleep
import re

log = jenkinsapi.job.log
SLEEP_RE = re.compile(r'Expires in (?P<seconds>\d+)(\,(?P<fractions>\d+))? sec')

class JenkinsException(Exception):
    pass

class JenkinsUnknownJobException(JenkinsException):
    pass

class JenkinsUnknownBuildException(JenkinsException):
    pass

class JenkinsDownException(JenkinsException):
    pass

def get_test_results(submission):
    server = get_server(submission.exercise)
    try:
        try:
            job = server[submission.exercise.jenkins_exercise.job]
        except UnknownJob:
            raise JenkinsUnknownJobException
        if submission.jenkins_result.build_number is None:
            raise JenkinsUnknownBuildException
        try:
            build = job.get_build(submission.jenkins_result.build_number)
        except KeyError:
            raise JenkinsUnknownBuildException
        if not build.has_resultset():
            return None, build.baseurl
        return build.get_data("{0:s}/{1:s}".format(build.baseurl, 
                                                   build.python_api_url("testReport"))), build.baseurl
    except requests.ConnectionError:
        raise JenkinsDownException


def get_server(exercise):
    """ Returns jenkinsapi.jenkins.Jenkins object for selected exercise """
    try:
        server = jenkinsapi.jenkins.Jenkins(exercise.jenkins_exercise.baseurl,
                                            username=exercise.jenkins_exercise.username,
                                            password=exercise.jenkins_exercise.password)
    except requests.ConnectionError:
        raise JenkinsDownException
    return server

def build_job(server, jobname, token, params):
    """ Builds job on server. Returns build_id and if build was successful """
    # TODO: Error handling
    Job.invoke = _invoke
    job = server.get_job(jobname)
    invoke = job.invoke(securitytoken=token, build_params=params)
    build_id = _wait_for_job(job, invoke)
    successful = _build_result(job, build_id)
    return build_id, successful

def _build_result(job, build_id):
    """ Checks build result for given job and build_id """
    # TODO: Error handling
    job.poll()
    build = job.get_build(build_id)
    while build.is_running():
        sleep(10)
    return build.is_good()

def _sleep_time(data, sleep_time):
    """ Tries to extract sleep time from data """
    if 'why' in data and data['why'] is not None:
        match = SLEEP_RE.search(data['why'])
        if match is not None:
            return int(match.group('seconds')) + 5
    sleep_time += 5 if sleep_time < 30 else 0
    return sleep_time

def _wait_for_job(job, invocation, max_time=10*60):
    """ Wait for job to finish executing """
    # TODO: Error handling
    sleep_time = 5
    total_time = sleep_time
    sleep(sleep_time)
    url = invocation.response.headers['location']
    data = job.get_data("{0:s}/api/python".format(url))
    while 'executable' not in data:
        if total_time >= max_time:
            return None
        sleep_time = _sleep_time(data, sleep_time)
        sleep(sleep_time)
        total_time += sleep_time
        data = job.get_data("{0:s}/api/python".format(url))

    return data['executable']['number']


def _invoke(self, securitytoken=None, block=False, skip_if_running=False, invoke_pre_check_delay=3,
           invoke_block_delay=15, build_params=None, cause=None, files=None):
    """ Temporarily monkeypatch jenkinsapi, because it doesn't correctly check
    for build id """
    
    assert isinstance(invoke_pre_check_delay, (int, float))
    assert isinstance(invoke_block_delay, (int, float))
    assert isinstance(block, bool)
    assert isinstance(skip_if_running, bool)

    # Create a new invocation instance
    invocation = Invocation(self)

    # Either copy the params dict or make a new one.
    build_params = build_params and dict(
        build_params.items()) or {}  # Via POSTed JSON
    params = {}  # Via Get string

    with invocation:
        if len(self.get_params_list()) == 0:
            if self.is_queued():
                raise WillNotBuild('%s is already queued' % repr(self))

            elif self.is_running():
                if skip_if_running:
                    log.warn(
                        "Will not request new build because %s is already running", self.name)
                else:
                    log.warn(
                        "Will re-schedule %s even though it is already running", self.name)
        elif self.has_queued_build(build_params):
            msg = 'A build with these parameters is already queued.'
            raise WillNotBuild(msg)

        log.info("Attempting to start %s on %s", self.name, repr(
            self.get_jenkins_obj()))

        url = self.get_build_triggerurl()
        # If job has file parameters - it must be triggered
        # using "/build", not by "/buildWithParameters"
        # "/buildWithParameters" will ignore non-file parameters
        if files:
            url = "%s/build" % self.baseurl

        if cause:
            build_params['cause'] = cause

        if securitytoken:
            params['token'] = securitytoken

        build_params['json'] = self.mk_json_from_build_parameters(build_params, files)
        data = build_params

        response = self.jenkins.requester.post_and_confirm_status(
            url,
            data=data,
            params=params,
            files=files,
            valid=[200, 201]
        )
        invocation.response = response
        if invoke_pre_check_delay > 0:
            log.info(
                "Waiting for %is to allow Jenkins to catch up", invoke_pre_check_delay)
            sleep(invoke_pre_check_delay)
        if block:
            total_wait = 0

            while self.is_queued():
                log.info(
                    "Waited %is for %s to begin...", total_wait, self.name)
                sleep(invoke_block_delay)
                total_wait += invoke_block_delay
            if self.is_running():
                running_build = self.get_last_build()
                running_build.block_until_complete(
                    delay=invoke_pre_check_delay)
    return invocation
