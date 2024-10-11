# Multi-Agent Reasoning Problem Solver (MAR-PS)

MAR-PS is a multi-agent reasoning problem solver. You build teams and they work together to solve the problems you give them.

You can work with them as a member of their team.

## Install

It can be installed via `pip` with the following command:
`pip install mar-ps`

Try the example in `example.py` to see it in action!

## Backends

Currently, MAR-PS supports both Ollama and OpenAI as backends.
Via the OpenAI backend, you can also use LM Studio models when the LM Studio server is on. Many different systems support the OpenAI API format.

We plan to add support for other backends, such as `MLX` or `transformers` in the future.

## Usage

Here is an example using an Ollama backend. Fist, let's setup the Ollama client and use it to create a model.

```py
from mar_ps import (
    OllamaClient,  # Ollama API client
    MAR,           # Multi-Agent Reasoning system class
    Model,         # the model class
    system,        # the system entity, for giving the initial system prompt
    Message,       # the message class
)

ollama_client = OllamaClient()

model = Model("llama3.1", ollama_client)
```

Note, you can have some models from one backend and some from another. For example, you could have Claude 3.5 Sonnet as a coding expert and a local model for creativity. (Claude runs on the OpenAI client).
Next, let's create the MAR and add some entities.

```py
mar = MAR(model) # This sets the default model.

logic_expert = mar.Entity(
    "Logic Expert",
    "an expert in logic and reasoning", # lowercase first letter and no end punctuation. See the system prompt to understand why.
)
math_expert = mar.Entity(
    "Math Expert",
    "an expert in math and solving problems",
)
```

In practice, you will likely want to use different models for different entities to play to their strengths. Now, make sure to add a user entity.

```py
user = mar.Entity(
    "Instruction Giver",
    "the one who gives problems and instructions, only message this user if you have the answer",
    "",
    is_user=True,
    pin_to_all_models=True, # all messages sent by this user will be pinned for all models to see.
)
```

By setting `is_user=True`, whenever a message is sent to the user, you will be prompted to respond.

Now let's give them a system prompt. Make sure to tell them who is on their team and who they are. If you don't do this, it won't work. I have found the following system prompt to work the best.

```py
for entity in mar.entities:
    entity.message_stack.append(
        Message(
            system,
            entity,
            f"This is the messaging application. Your team includes: {'\n'.join([f'{e.id}: {e.introduction[0].upper()+e.introduction[1:]}.' for e in mar.entities if e != entity])}. You may address messages to any of them and receive messages from any of them. You may not send messages to anyone outside of your team. Your messages are private; only the sender and receiver can see them. Thus, you will need to share information with your teammates. There can only be one recipient per message, the messaging application does not support sending messages to multiple recipients at once. You are {entity.id}, {entity.introduction}. {entity.personal_prompt + " " if entity.personal_prompt else ''}Messages sent by you are started with To: and messages sent to you are started with From:.",
        )
    )
```

And finally start the chat by sending a message.

```py
mar.start(logic_expert.send(input("You: "), user))
```

If we set `print_all_messages` to `True` in the `send` method, it would allow us to see all the messages sent. Otherwise, we will only see the messages sent to the user, which is fine for this example.

See `simple_example.py` for the full code.

## API Reference

### `Client`

Client base class from which `OpenAIClient` and `OllamaClient` inherit.

#### `async Client.get_chat_completion(self, messages: list[MessageDict], model_id: str, options={}) -> str`

Gets a chat completion from the client.

### `OpenAIClient(Client)`

#### `OpenAIClient.__init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, **kwargs)`

Initializes the OpenAI client. kwargs are passed to `openai.OpenAI.__init__`.

#### `async OpenAIClient.get_chat_completion(self, messages, model_id: str = "gpt-4o-mini", options={}) -> str`

Gets a chat completion from the client. Default model is `gpt-4o-mini`.

#### `OpenAIClient.openai`

The `openai.OpenAI` instance.

### `OllamaClient(Client)`

#### `OllamaClient.__init__(self, host: Optional[str] = None, **kwargs)`

Initializes the Ollama client with the given host. `kwargs` are passed to `ollama.AsyncClient`.

#### `async OllamaClient.get_chat_completion(self, messages, model_id: str = "gpt-4o-mini", options={}) -> str`

### `Model`

#### `Model.__init__(self, id: str, client: Client)`

Initializes the model.

#### `async Model.generate(self, messages: list[Message], options={})`

Generates a response from the model.

#### `Model.id`

The model ID.

#### `Model.client`

The model client, a `Client` object.

### `EntityName`

An entity name.

#### `EntityName.__init__(self, id: str, pin_to_all_models: bool = False)`

Initializes the entity name.

#### `EntityName.id`

The name of the entity

#### `EntityName.pin_to_all_models`

If true, all messages made by this entity will be given to all models, not just the recipient.

### `System(EntityName)`

The `system` entity name is a instance of this class and is used for system prompts.

#### `system.id`

The system name, always equal to `"system"`.

### `Mar`

The `MAR` class.

#### `MAR.__init__(self, global_default_model: Optional[Model] = None)`

Initializes the MAR. The global default model is used for all entities in this MAR that don't have a model assigned.

#### `Mar.Entity(self, id: str, introduction: str, personal_prompt: str = "", model: Optional[Model] = None, temperature: float = 0.5, is_user: bool = False, pin_to_all_models: bool = False,)`

Creates an entity with the given arguments.
`id`: The ID/Name of the entity.
`introduction`: The introduction of the entity. This is generally a single sentence with no end punctuation or capitalization. See the example system prompt for why.
`model`: The model to be used in generation. If not specified, the MAR's global default model is used.
`temperature`: The temperature to be used in generation. Defaults to 0.5.
`options`: A list of other options to be used. These are client-specific.
`is_user`: If true, the user will be prompted to respond via stdin instead of generating with the model.
`pin_to_all_models`: If true, all messages this model sends will be pinned to the context for all other models. But only the model the message was sent to will get a chance to respond.

#### `MAR.start(self, func)`

Starts the MAR. `func` is meant to be a `Entity.send()` method.

#### `MAR.entities`

The list of entities in this MAR.

#### `MAR.global_default_model`

The global default model for this MAR.

### `Entity(EntityName)`

A class derived from `EntityName` that represents an entity and includes methods for generating responses and sending messages.

#### `Entity.__init__(self, mar: MAR, id: str, introduction: str, personal_prompt: str = "", model: Optional[Model] = None, temperature: float = 0.5, options: dict = {}, is_user: bool = False, pin_to_all_models: bool = False)`

Initializes the entity. Please use `MAR.Entity()` instead. See reference there for information on parameters.

#### `Entity.generate(self, stream: bool = False)`

Generates a response from the entity.
Streaming is not supported, but the parameter is there. If set to true, you will get a `NotImplementedError`.

#### `Entity.send(self, message: Message | str | None = None, sender: Optional[EntityName] = None, print_all_messages: bool = False, max_errors_before_handling: int = 3,error_handling_mode: Literal["resend", "resend-empty-message", "quit"] = "resend", message_handler: Optional[Callable] = None)`

Sends a message to the entity.
`message`: The message to send. May be a `Message` object (which includes information such as sender or recipient), or a string. If it is a string, the `sender` parameter is required.
`sender`: The sender of the message. This is only used if `message` is a string.
`print_all_messages`: If true, all messages sent in this and subsequent generations will be printed. Defaults to false. Useful if you want to see what they are talking about behind the scenes.
`max_errors_before_handling`: The maximum number of errors before the message is handled. Defaults to 3.
`error_handling_mode`: The mode of error handling. Default: `resend`. Options:

- `resend`: if the model produced a message but no recipient, it will be sent back to the entity that it is responding to.
- `resend-empty-message`: an empty message will be returned to the entity that it is responding to.
- `quit`: A `RuntimeError` will be raised.

`message_handler`: If provided, this function will be called with the message as an argument. This can be useful for custom logging or other purposes.
`message_processor`: If provided, this function will be called with the message as an argument. It is expected to return a `Message`, which will replace the original message.

#### `Entity.mar`

The MAR that this entity belongs to.

#### `Entity.model`

The model that this entity uses.

#### `Entity.introduction`

A short, single sentence introduction of this entity. It should have no ending punctuation or starting capitalization.

#### `Entity.personal_prompt`

A personal prompt for this entity. Tell the entity how to act and respond.

#### `Entity.temperature`

The temperature that the entity uses in generation.

#### `Entity.options`

The options for generation. This is model and client-specific.

#### `Entity.is_user`

If true, the you will be prompted to respond via stdin rather than having the model generate a response.

#### `Entity.pin_to_all_models`

If true, all messages this model sends will be pinned to the context for all other models. But only the model the message was sent to will get a chance to respond.

#### `Entity.id`

The ID/Name of the entity.

#### `Entity.message_stack`

The message stack of the entity.

### `Message`

#### `Message.__init__(self, sender: EntityName, recipient: EntityName, content: str)`

Initializes the message.

#### `Message.format(self, format_for: Optional[EntityName] = None)`

Formats the message into dictionary form to be used as context for the `format_for` entity.

#### `Message.clone(self, sender: Optional[EntityName] = None, recipient: Optional[EntityName] = None, content: Optional[str] = None)`

Clones the message with the applied differences.

#### `Message.sender`

The sender of the message. An `EntityName` object.

#### `Message.recipient`

The recipient of the message. An `EntityName` object.

#### `Message.content`

The content of the message. A string

### `get_element(lst: list, index: int, default: Any = None)`

Returns the element at the given index in the list. If the index is out of range, returns the default value.

### `extract_name_and_content(message: str)`

Extracts the name and content from the generated message.

## TODO

### Features to add

- Tool support

- Streaming support (This can be used to catch incorrect formatting earlier on)

- RAG support

- Memory support to save important information

- Cross-conversation learning

- Test Cases to make sure everything works before publishing

### Backends to add

- MLX-ENGINE (<https://github.com/lmstudio-ai/mlx-engine/>)
- Transformers (<https://github.com/huggingface/transformers/>)
- CoreML (<https://github.com/apple/coremltools/>)

### Hard ones to add

- Support for multi-recipient messages

- Support for multi-message responses

NOTE: These will be VERY difficult to implement because every time an entity receives a message, it tries to reply. If you send a message to many entities, they will all try to reply.

- Image input support
