#### Multi-Agent Reasoning Problem Solver


from typing import Union, Literal, Optional, TypedDict, Any, Callable
import asyncio
import openai
import ollama


# ollama = None
# openai = None


Messages = []


class MessageDict(TypedDict):
    role: Literal["user", "assistant", "system", "tool"]
    content: str


class Client:

    async def get_chat_completion(self, messages, model_id: str, options={}) -> str:
        return "none"


class OpenAIClient(Client):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        # global openai
        # if openai == None:
        #     try:
        #         openai = __import__("openai")
        #     except ImportError:
        #         raise ImportError(
        #             "OpenAI API client not found. You may be able to fix this by running `pip install openai`"
        #         )

        self.openai = openai.OpenAI(api_key=api_key, base_url=base_url, **kwargs)

    async def get_chat_completion(
        self, messages, model_id: str = "gpt-4o-mini", options={}
    ):
        chat_completion = self.openai.chat.completions.create(
            model=model_id,
            messages=messages,
            stop=["From:", "\nTo:"],
            **options,
        )
        return chat_completion.choices[0].message.content or ""


class OllamaClient(Client):
    def __init__(self, host: Optional[str] = None, **kwargs):
        self.ollama = ollama.AsyncClient(host, **kwargs)
        # global ollama
        # if ollama == None:
        #     try:
        #         ollama = __import__("ollama")
        #     except ImportError:
        #         raise ImportError(
        #             "Ollama API client not found. You may be able to fix this by running `pip install ollama`"
        #         )

    async def get_chat_completion(
        self, messages, model_id: str = "gpt-4o-mini", options={}
    ) -> str:
        response = await self.ollama.chat(
            model_id,
            messages,
            options={
                "temperature": options.get("temperature", 0.8),
                "stop": ["From:", "\nTo:"],
                "use_mmap": False,
                "logits_all": True,
            },
            stream=False,
        )
        return response["message"]["content"]


class Model:
    id: str
    client: Client

    def __init__(self, id: str, client: Client):

        self.id = id
        self.client = client

    async def generate(self, messages: list["Message"], options={}) -> str:
        return await self.client.get_chat_completion(messages, self.id, options)


def extract_name_and_content(message: str):
    # Find the start index of the name, which is after 'To: '
    start_index = message.find("To: ") + 4
    if start_index == 3:  # 'To: ' not found
        return None, None

    # Find the index of the newline after the name
    end_index = message.find("\n", start_index)

    # Extract the name
    name = message[start_index:end_index]

    # Extract the message content (everything after the newline)
    content = message[end_index + 1 :]  # Skip the newline character

    return name.strip(), content.strip("\n\t ")


def get_element(lst: list, index: int, default: Any = None):
    try:
        return lst[index]
    except IndexError:
        return default


class EntityName:

    def __init__(self, id: str, pin_to_all_models: bool = False):
        self.id = id
        self.pin_to_all_models = pin_to_all_models


class System(EntityName):
    id = "system"

    def __init__(self):
        super().__init__(self.id)


system = System()


class MAR:
    entities: list["Entity"]
    global_default_model: Optional[Model]

    def __init__(self, global_default_model: Optional[Model] = None):
        self.global_default_model = global_default_model
        self.entities = []

    def Entity(
        self,
        id: str,
        introduction: str,
        personal_prompt: str = "",
        model: Optional[Model] = None,
        temperature: float = 0.5,
        options: dict = {},
        is_user: bool = False,
        pin_to_all_models: bool = False,
    ):
        return Entity(
            self,
            id,
            introduction,
            personal_prompt,
            model,
            temperature,
            options,
            is_user,
            pin_to_all_models,
        )

    def start(self, func):
        asyncio.run(func)


class Entity(EntityName):
    model: Optional[Model]

    def __init__(
        self,
        mar: MAR,
        id: str,
        introduction: str,
        personal_prompt: str = "",
        model: Optional[Model] = None,
        temperature: float = 0.5,
        options: dict = {},
        is_user: bool = False,
        pin_to_all_models: bool = False,
    ):
        self.mar = mar
        model = model if model != None else mar.global_default_model
        if model == None and is_user == False:
            raise ValueError("Entity model cannot be None")
        else:
            self.model = model
        self.id = id
        self.introduction = introduction
        self.personal_prompt = personal_prompt
        self.temperature = temperature
        self.options = options
        self.is_user = is_user
        self.message_stack = []
        self.pin_to_all_models = pin_to_all_models
        mar.entities.append(self)

    async def generate(self, stream: bool = False):
        if stream:
            raise NotImplementedError("Response streaming is not yet supported")
        if self.model == None:
            raise ValueError("Entity model cannot be None")
        return await self.model.generate(
            [message.format(self) for message in self.message_stack],
            {"temperature": self.temperature, **self.options},
        )

    async def send(
        self,
        message: Union["Message", str, None] = None,
        sender: Optional[EntityName] = None,
        print_all_messages: bool = False,
        max_errors_before_handling: int = 3,
        error_handling_mode: Literal[
            "resend", "resend-empty-message", "quit"
        ] = "resend",
        message_handler: Optional[Callable[["Message"], Any]] = None,
        message_processor: Optional[Callable[["Message"], "Message"]] = None,
    ):
        if message != None:
            if sender == None and type(message) == Message and message.sender != None:
                sender = message.sender
            if isinstance(message, str):
                if not sender:
                    sender = EntityName("anonymous")
                message = Message(sender, self, message)
            if type(message.sender) != System and message.sender.pin_to_all_models:
                for entity in self.mar.entities:
                    m = message.clone(recipient=entity)
                    entity.message_stack.append(m)
            else:
                self.message_stack.append(message)
            if sender:
                if print_all_messages:
                    print(
                        f"\x1b[32mMessage sent from {sender.id} to {self.id}:\x1b[0m\n{message.content}\n"
                    )
                else:
                    print(f"\x1b[32mMessage sent from {sender.id} to {self.id}.\x1b[0m")
        if message and message_handler:
            message_handler(message)
        if message and message_processor:
            message = message_processor(message)
        response = ""
        last_error_count = 0
        while True:
            if (
                last_error_count >= max_errors_before_handling
                or max_errors_before_handling <= 0
            ):
                if print_all_messages:
                    print(
                        f"\x1b[31mError: too many errors. Handling according to rule {error_handling_mode}.\x1b[0m"
                    )
                if error_handling_mode == "raise":
                    raise RuntimeError(
                        f"Entity {self.id}, model {(self.model or self.mar.global_default_model or EntityName('unknown')).id}: too many errors. Quitting."
                    )
                else:
                    recipient = [
                        ent
                        for ent in [
                            sender,
                            message.sender if message else None,
                            self.mar.entities[0],
                        ]
                        if ent
                        and isinstance(
                            ent, Entity
                        )  # Must be an Entity that can be responded to.
                    ][0]
                    if (
                        response == None
                        or error_handling_mode == "resend-empty-message"
                    ):
                        response = ""
                    break
            if self.is_user:
                if sender and message:
                    print(f"\x1b[31mAI ({sender.id}): \x1b[0m{message.content}")
                raw_response = input("\x1b[31mYou: \x1b[0m").replace("\\n", "\n")
                if not raw_response.startswith("To:") and sender:
                    raw_response = f"To: {sender.id}\n" + raw_response
            else:
                raw_response = (await self.generate()).strip(" \t\n")
            recipient_name, response = extract_name_and_content(raw_response)
            if recipient_name is None or response is None:
                error = "Error: no recipient name found. Remember to begin your messages with To:"
                if print_all_messages:
                    print(raw_response)
                    print(f"\x1b[31m{error}\x1b[0m")
                if last_error_count > 0:
                    self.message_stack[-1].content = error
                else:
                    self.message_stack.append(
                        Message(EntityName("system"), self, error)
                    )
                last_error_count += 1
            else:
                recipient = get_element(
                    [
                        entity
                        for entity in self.mar.entities
                        if entity.id.lower().replace(" ", "-").replace("_", "-")
                        == recipient_name.lower().replace(" ", "-").replace("_", "-")
                    ],
                    0,
                    None,
                )
                if recipient is None:
                    error = f'Error: recipient not found: "{recipient_name}". Remember, you may only message members of your team.'
                    if (
                        "," in recipient_name
                        or "&" in recipient_name
                        or recipient_name in ["all", "team"]
                    ):
                        error += (
                            " Currently, only one recipient per message is supported."
                        )
                    if print_all_messages:
                        print(raw_response)
                        print(f"\x1b[31m{error}\x1b[0m")
                    if last_error_count > 0:
                        self.message_stack[-1].content = error
                    else:
                        self.message_stack.append(
                            Message(EntityName("system"), self, error)
                        )
                    last_error_count += 1

                else:
                    break
        response_message = Message(self, recipient, response)
        self.message_stack.append(response_message)
        task = asyncio.create_task(
            recipient.send(
                response_message,
                self,
                print_all_messages,
                max_errors_before_handling,
                error_handling_mode,
                message_handler,
                message_processor,
            )
        )
        await task
        return response

    def __str__(self):
        return f"<Entity: {self.id}>"

    __repr__ = __str__


class Message:

    def __init__(
        self,
        sender: EntityName,
        recipient: EntityName,
        content: str,
    ):
        self.sender = sender
        self.recipient = recipient
        self.content = content
        Messages.append(self)

    def __str__(self):
        return f"<Message from {self.sender} to {self.recipient}: {self.content}>"

    __repr__ = __str__

    def format(self, format_for: Optional[EntityName] = None) -> MessageDict:
        if self.sender == system:
            return {"role": "system", "content": self.content}
        elif format_for == self.sender:
            return {
                "role": "assistant",
                "content": f"To: {self.recipient.id}\n{self.content}",
            }
        elif format_for == self.recipient:
            return {
                "role": "user",
                "content": f"From: {self.sender.id}\n{self.content}",
            }
        else:
            return {
                "role": "user",
                "content": f"From: {self.sender.id}\nTo: {self.recipient.id}\n{self.content}",
            }

    def clone(
        self,
        sender: Optional[EntityName] = None,
        recipient: Optional[EntityName] = None,
        content: Optional[str] = None,
    ):
        return Message(
            sender or self.sender, recipient or self.recipient, content or self.content
        )
