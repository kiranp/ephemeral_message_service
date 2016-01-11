from rest_framework import serializers

from restapi.models import Chat

#Serializers allow complex data such as querysets and model instances
# to be converted to native Python datatypes that can then be easily
# rendered into JSON, XML or other content types. Serializers also
# provide deserialization, allowing parsed data to be converted back
# into complex types, after first validating the incoming data.

class ChatPOSTSerializer(serializers.ModelSerializer):
    """
    Serializer to handle POST data
    """
    class Meta:
        model = Chat
        fields = ('id', 'username', 'text', 'timeout', 'expiration_date')

class ChatGETIDSerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve a single Chat message and display only id
    """
    class Meta:
        model = Chat
        fields = ('id',)

class ChatGETSerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve a single Chat message and display only username,
    text and expiration_date columns.
    """
    class Meta:
        model = Chat
        fields = ('username', 'text', 'expiration_date')

class ChatGETUserSerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve Chat messages of a given user. Displays just the
    id and text columns.
    """
    class Meta:
        model = Chat
        fields = ('id', 'text')
