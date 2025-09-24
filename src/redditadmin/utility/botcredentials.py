class BotCredentials:
    """
    Class holding the bot's credentials
    """

    __user_agent: str
    __client_id: str
    __client_secret: str
    __username: str
    __password: str

    def __init__(
            self,
            user_agent,
            client_id,
            client_secret,
            username,
            password
    ):
        self.__user_agent = user_agent
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__username = username
        self.__password = password

    @property
    def get_user_agent(self):
        """Retrieve the bot's User Agent"""

        return self.__user_agent

    @property
    def get_client_id(self):
        """Retrieve the bot's Client ID"""

        return self.__client_id

    @property
    def get_client_secret(self):
        """Retrieve the bot's Client Secret"""

        return self.__client_secret

    @property
    def getusername(self):
        """Retrieve the bot's Username"""

        return self.__username

    @property
    def get_password(self):
        """Retrieve the bot's Password"""

        return self.__password

    def clear_credentials(self):
        """Convenience method to clear the bot's credentials"""

        self.__user_agent = ""
        self.__client_id = ""
        self.__client_secret = ""
        self.__username = ""
        self.__password = ""
