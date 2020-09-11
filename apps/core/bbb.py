#
# Darasa LMS BBB Python Wrapper
# Author: Antony Orenge (@antorenge)
# @version: Big Blue Button API v2.2
#
# flake8: noqa: E401
# flake8: noqa: E722

import xmltodict
import urllib.request
import urllib.parse
import urllib.error
import socket
import hashlib
import random


def bbb_wrap_load_file(url):
    timeout = 10
    socket.setdefaulttimeout(timeout)

    try:
        req = urllib.request.urlopen(url)
        reqdict = xmltodict.parse(req.read())
        return dict(reqdict.get("response"))
    except:
        return False


def join_meeting_url(
    meeting_id, full_name, user_id, password, URL, SALT, redirect=True, **kwargs
):
    """This method returns the url to join the specified meeting.

    @param meeting_id -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param full_name -- the display name to be used when the user joins the meeting
    @param user_id -- An identifier for this user that will help your application to identify which person this is.
    @param password -- the attendee or moderator password of the meeting
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server
    @param create_time -- This prevents a user from reusing their join URL for a subsequent session with the same meetingID.
    @param redirect --

    @return The url to join the meeting
    """
    url_join = URL + "api/join?"

    parameters = {
        "meetingID": meeting_id,
        "fullName": full_name,
        "userID": user_id,
        "password": password,
        "redirect": redirect,
    }
    parameters.update(dict((k, v) for k, v in kwargs.items() if v is not None))

    parameters = urllib.parse.urlencode(parameters)

    return (
        url_join
        + parameters
        + "&checksum="
        + hashlib.sha1(("join" + parameters + SALT).encode("utf-8")).hexdigest()
    )


def create_meeting_url(
    name,
    meetingID,
    attendeePW,
    moderatorPW,
    welcome,
    logoutURL,
    callback_url,
    URL,
    SALT,
    duration=0,
    allow_start_stop_recording=True,
    auto_start_recording=False,
    **kwargs
):
    """This method returns the url to join the specified meeting.

    @param name -- a name fot the meeting
    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param attendeePW -- the attendee of the meeting
    @param moderatorPW -- the moderator of the meeting
    @param welcome -- the welcome message that gets displayed on the chat window
    @param logoutURL -- the URL that the bbb client will go to after users logouut
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return The url to join the meeting
    """
    url_create = URL + "api/create?"
    voiceBridge = 70000 + random.randint(0, 9999)
    parameters = {
        "name": name,
        "meetingID": meetingID,
        "attendeePW": attendeePW,
        "moderatorPW": moderatorPW,
        "voiceBridge": voiceBridge,
        "logoutURL": logoutURL,
        "meta_endCallbackUrl": callback_url,
        "duration": duration,
        "allowStartStopRecording": allow_start_stop_recording,
        "autoStartRecording": auto_start_recording,
    }
    parameters.update(dict((k, v) for k, v in kwargs.items() if v is not None))

    parameters = urllib.parse.urlencode(parameters)

    return (
        url_create
        + parameters
        + "&checksum="
        + hashlib.sha1(("create" + parameters + SALT).encode("utf-8")).hexdigest()
    )


def is_meeting_running_url(meetingID, URL, SALT):
    """This method returns the url to check if the specified meeting is running.

    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return The url to check if the specified meeting is running.
    """
    base_url = URL + "api/isMeetingRunning?"

    parameters = {"meetingID": meetingID}
    parameters = urllib.parse.urlencode(parameters)

    return (
        base_url
        + parameters
        + "&checksum="
        + hashlib.sha1(
            ("isMeetingRunning" + parameters + SALT).encode("utf-8")
        ).hexdigest()
    )


def get_meeting_info_url(meetingID, modPW, URL, SALT):
    """This method returns the url to get_meeting_info of the specified meeting.

    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param modPW -- the moderator password of the meeting
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return The url to check if the specified meeting is running.
    """
    base_url = URL + "api/getMeetingInfo?"

    parameters = {"meetingID": meetingID, "password": modPW}
    parameters = urllib.parse.urlencode(parameters)

    return (
        base_url
        + parameters
        + "&checksum="
        + hashlib.sha1(
            ("getMeetingInfo" + parameters + SALT).encode("utf-8")
        ).hexdigest()
    )


def get_meetings_url(URL, SALT):
    """This method returns the url for listing all meetings in the bigbluebutton server.

    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return The url of get_meetings.
    """
    base_url = URL + "api/getMeetings?"

    parameters = {"random": (random.random() * 1000)}
    parameters = urllib.parse.urlencode(parameters)

    return (
        base_url
        + parameters
        + "&checksum="
        + hashlib.sha1(("getMeetings" + parameters + SALT).encode("utf-8")).hexdigest()
    )


def end_meeting_url(meetingID, modPW, URL, SALT):
    """This method returns the url to end the specified meeting.

    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param modPW -- the moderator password of the meeting
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return The url to end the specified meeting.
    """
    base_url = URL + "api/end?"

    parameters = {"meetingID": meetingID, "password": modPW}
    parameters = urllib.parse.urlencode(parameters)

    return (
        base_url
        + parameters
        + "&checksum="
        + hashlib.sha1(("end" + parameters + SALT).encode("utf-8")).hexdigest()
    )


def create_meeting(
    name,
    meeting_id,
    moderator_pw,
    attendee_pw,
    welcome_message,
    logout_url,
    callback_url,
    url,
    secret,
    duration=0,
    allow_start_stop_recording=True,
    auto_start_recording=False,
    **kwargs
):
    """This method creates a meeting and return an array of the xml packet

    @param name
    @param meeting_id -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param moderator_pw -- the moderator password of the meeting
    @param attendee_pw -- the attendee password of the meeting
    @param welcome_message -- the welcome message to be displayed when a user logs in to the meeting
    @param logoutURL -- the url the user should be redirected to when they logout of bigbluebutton
    @param logout_url
    @param callback_url
    @param url
    @param secret
    @param duration -- Default duration of the meeting in minutes. Current default is 0 (meeting doesn't end).
    @param allow_start_stop_recording
    @param auto_start_recording

    @return
        - Null if unable to reach the bigbluebutton server
        - False if an error occurs while parsing
        - Dictionary containing the values of the xml packet
    """
    create_url = create_meeting_url(
        name,
        meeting_id,
        attendee_pw,
        moderator_pw,
        welcome_message,
        logout_url,
        callback_url,
        url,
        secret,
        duration,
        allow_start_stop_recording,
        auto_start_recording,
        **kwargs
    )

    response = bbb_wrap_load_file(create_url)
    if response:
        return response

    # if unable to reach the server
    return {}


def get_meeting_info(meetingID, modPW, URL, SALT):
    """This method calls the get_meeting_info on the bigbluebutton server and returns an array.

    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param modPW -- the moderator password of the meeting
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return
        - None if unable to reach the bigbluebutton server
        - Dictionary containing the values of the xml packet
            - If the returncode == 'FAILED' it returns a dictionary containing a returncode, messagekey, and message.
            - If the returncode == 'SUCCESS' it returns a dictionary containing a meetingID, moderatorPW, attendeePW,
                hasBeenForciblyEnded, running, startTime, endTime, participantCount, moderatorCount, and attendees.
    """
    _get_meeting_info_url = get_meeting_info_url(meetingID, modPW, URL, SALT)
    response = bbb_wrap_load_file(_get_meeting_info_url)

    if response:
        return response

    # if unable to reach the server
    return {}


def get_meetings(URL, SALT):
    """This method calls get_meetings on the bigbluebutton server,
    then calls get_meeting_info for each meeting and concatenates the result.

    @param URL -- the url of the bigbluebutton server
    @param SALT -- the security salt of the bigbluebutton server

    @return
        - None if unable to reach the bigbluebutton server
        - Dictionary containing the values of the xml packet
            - If the returncode == 'FAILED' it returns a dictionary containing a returncode, messagekey, and message.
            - If the returncode == 'SUCCESS' it returns a dictionary containing all the meetings. Each item  meetingID, moderatorPW, attendeePW,
                hasBeenForciblyEnded, running, startTime, endTime, participantCount, moderatorCount, and attendees.

        - Null if the server is unreachable
        - If FAILED then returns an array containing a returncode, messageKey, message.
        - If SUCCESS then returns an array of all the meetings. Each element in the array is an array containing a meetingID,
            moderatorPW, attendeePW, hasBeenForciblyEnded, running.
    """
    _get_meetings_url = get_meetings_url(URL, SALT)
    response = bbb_wrap_load_file(_get_meetings_url)

    if response:
        return response

    # if unable to reach the server
    return {}


def end_meeting(meetingID, modPW, URL, SALT):
    """This method calls end meeting on the specified meeting in the bigbluebutton server.

    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param modPW -- the moderator password of the meeting
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return
        - {} if the server is unreachable
        - A dictionary containing a returncode, messageKey, message.
    """
    _end_meeting_url = end_meeting_url(meetingID, modPW, URL, SALT)
    response = bbb_wrap_load_file(_end_meeting_url)

    if response:
        return response

    # if unable to reach the server
    return {}


def is_meeting_running(meetingID, URL, SALT):
    """This method check the BigBlueButton server to see if the meeting is running
    (i.e. there is someone in the meeting)

    @param meetingID -- the unique meeting identifier used to store the meeting in the bigbluebutton server
    @param SALT -- the security salt of the bigbluebutton server
    @param URL -- the url of the bigbluebutton server

    @return A boolean of true if the meeting is running and false if it is not running
    """
    _is_meeting_running_url = is_meeting_running_url(meetingID, URL, SALT)
    response = bbb_wrap_load_file(_is_meeting_running_url)

    if response:
        return response

    # if unable to reach the server
    return {}
