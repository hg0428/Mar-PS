from mar_ps import (
    OllamaClient,  # Ollama API client
    MAR,  # Multi-Agent Reasoning system class
    Model,  # the model class
    system,  # the system entity, for giving the initial system prompt
    Message,  # the message class
)

ollama_client = OllamaClient()

model = Model("llama3.1", ollama_client)

mar = MAR(model)  # This sets the default model.

logic_expert = mar.Entity(
    "Logic Expert",
    "an expert in logic and reasoning",  # lowercase first letter and no end punctuation. See the system prompt to understand why.
)
math_expert = mar.Entity(
    "Math Expert",
    "an expert in math and solving problems",
)

user = mar.Entity(
    "User",
    "the one who gives problems and instructions",
    "",
    is_user=True,
    pin_to_all_models=True,  # all messages sent by this user will be pinned for all models to see.
)


for entity in mar.entities:
    entity.message_stack.append(
        Message(
            system,
            entity,
            f"This is the messaging application. Your team includes: {'\n'.join([f'{e.id}: {e.introduction[0].upper()+e.introduction[1:]}.' for e in mar.entities if e != entity])}. You may address messages to any of them and receive messages from any of them. You may not send messages to anyone outside of your team. Your messages are private; only the sender and receiver can see them. Thus, you will need to share information with your teammates. There can only be one recipient per message, the messaging application does not support sending messages to multiple recipients at once. You are {entity.id}, {entity.introduction}. {entity.personal_prompt + " " if entity.personal_prompt else ''}Messages sent by you are started with To: and messages sent to you are started with From:.",
        )
    )


mar.start(logic_expert.send(input("You: "), user, print_all_messages=True))
