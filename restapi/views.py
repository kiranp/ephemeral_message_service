import logging

from datetime import datetime
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import UserRateThrottle
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from restapi.models import Chat
from EphemeralMessages.settings import CHAT_THROTTLE_RATE
from restapi.exceptions import handle_api_exceptions, EphemeralMessageError
from restapi.serializers import (ChatPOSTSerializer,
                                 ChatGETSerializer, ChatGETUserSerializer)

logger = logging.getLogger('CHAT')


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class OncePerDayUserThrottle(UserRateThrottle):
    rate = CHAT_THROTTLE_RATE


@api_view(['GET'])
def ephemeral_messages_service(request):
    """
    A simple ephemeral text message service.
    The service has three RESTful endpoints for accessing data:
    1. POST /chat
    Creates a new text message for passed in username.
    Request body properties:
        - username: String, The recipient of the message (required)
        - text: String, The content of the message (required)
        - timeout: Integer, The number of seconds the message
        should live before expiring (default 60)
    Response:
    A success response will include:
        - a status code of 201 Created
        - a body with a JSON object

    2. GET /chat/:id
    Returns the message object for the given id.
    Response:
    A success response will include:
        - a JSON object containing the message
        the message's username, text and expiration_date

    3. GET /chats/:username
    Returns a list of all unexpired texts for the user with the
    given username.
    Response:
    A success response will include:
        - a JSON array of messages, each of which contains the
        message's ID and text.

    """
    logger.debug("Home page requested")
    return Response({'description': 'EphemeralMessages API'})


@handle_api_exceptions
def set_cache(id, data, timeout):
    """
    Set cache key. Exceptions handled by decorator.
    :param id: key
    :param data: value
    :param timeout: timeout
    :return: None
    """
    logger.debug("Set id %s, data %s in cache with timeout %s"
                 %(id, data, timeout))
    cache.set(id, data, timeout)


@handle_api_exceptions
def expire_cache(id):
    """
    Expire cache key. Exceptions handled by decorator.
    :param id: key
    :return: None
    """
    logger.debug("Set expiration for id %s" %id)
    cache.expire(id, 0)


@handle_api_exceptions
def get_cache(id):
    """
    Get cache key. Exceptions handled by decorator.
    :param id: key
    :return: value
    """
    logger.debug("Get id %s from cache" %id)
    return cache.get(id)


@api_view(['POST'])
@throttle_classes([OncePerDayUserThrottle])
@handle_api_exceptions
@transaction.atomic
def create_message(request):
    """
    Creates a new text message for passed in username and text.

    POST /chat
    
    Sample json request body:
    {"username": <text>,
    "text": <text>,
    "timeout": <id>}

    """
    try:
        serializer = ChatPOSTSerializer(data=request.data)
        if serializer.is_valid():
            chat = serializer.save()
            chat_message = Chat.objects.get(id=chat.id)
            logger.debug("Created chat message %s" % repr(chat_message))
            cache_serializer = ChatGETSerializer(chat_message)
            set_cache(chat.id, cache_serializer.data, timeout = chat.timeout)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            logger.error("Post message is not valid %s" %
                         repr(serializer.data))
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
    except EphemeralMessageError as err:
        logger.error("Error processing message %s" % repr(err))
        return Response(EphemeralMessageError,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@handle_api_exceptions
def get_message(request, chat_id):
    """
    Returns the message object for the given id. This service can return both expired and unexpired messages.

    GET /chat/:id
    """
    try:
        chat_message = get_cache(chat_id)
        if not chat_message:
            chat_message = Chat.objects.get(id=chat_id)
            serializer = ChatGETSerializer(chat_message)
            logger.debug("Get chat message from db %s" % repr(serializer.data))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.debug("Get chat message from cache %s" % repr(chat_message))
            return Response(chat_message, status=status.HTTP_200_OK)
    except Chat.DoesNotExist as ex:
        logger.error("Chat id does not exist %s" % repr(ex))
        return Response("Chat id does not exist",
                        status=status.HTTP_400_BAD_REQUEST)
    except EphemeralMessageError as message_processing_error:
        logger.error("Error processing request for chat id %s"
                     % repr(message_processing_error))
        return Response(EphemeralMessageError,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@handle_api_exceptions
def get_user_messages(request, user_name):
    """
    Returns a list of all unexpired texts for the user with the given username. Any texts that are recieved are then expired.

    GET /chats/:username
    """
    try:
        logger.debug("Extract chat messages for user %s" % repr(user_name))
        chat_messages = Chat.objects.filter(username=user_name,
                                            expiration_date__gt = datetime.now())
        serializer = ChatGETUserSerializer(chat_messages, many=True)
        for chat_message in chat_messages:
            chat_message.timeout = 0
            expire_cache(chat_message.id)
            chat_message.save()
        logger.debug("Processed chat messages for user %s" % repr(user_name))
        return Response(serializer.data, status=status.HTTP_200_OK)
    except EphemeralMessageError as message_processing_error:
        logger.error("Error processing request for user %s"
                     % repr(message_processing_error))
        return Response(EphemeralMessageError,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
