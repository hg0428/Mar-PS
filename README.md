# Multi-Agent Reasoning Problem Solver (MAR-PS)

MAR-PS is a multi-agent reasoning problem solver. You build teams and they work together to solve the problems you give them.

You can work with them as a member of their team.

## Install

It can be installed via `pip` with the following command:
`pip install mar-ps`

## Backends

Currently, MAR-PS supports both Ollama and OpenAI as backends. We plan to add support for other backends in the future.

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
    "User",
    "the one who gives problems and instructions",
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
mar.start(logic_expert.send(input("You: "), user, print_all_messages=True))
```

By setting `print_all_messages` to `True`, it allows us to see all the messages sent. Otherwise, we would only see the messages sent to the user.

See `simple_example.py` for the full code.

## TODO

### Features to add

- TODO: add tool support

- TODO: add streaming support

### Backends to add

- MLX-ENGINE (<https://github.com/lmstudio-ai/mlx-engine/>)
- Transformers (<https://github.com/huggingface/transformers/>)
- CoreML (<https://github.com/apple/coremltools/>)

### Hard ones to add

- TODO: add support for multi-recipient messages

- TODO: add support for multi-message responses

NOTE: These will be VERY difficult to implement because every time an entity receives a message, it tries to reply. If you send a message to many entities, they will all try to reply.
