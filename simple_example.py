from mar_ps import (
    Message,
    system,
    OllamaClient,
    OpenAIClient,
    Model,
    MAR,
)


ollama_client = OllamaClient()
openai_client = OpenAIClient()
mar = MAR()


team_leader = mar.Entity(
    "Team Leader",
    "the team lead who manages all communications with the competition manager and delegates tasks",
    "",
    # Model("gpt-4o-mini", openai_client),  # OpenAI
    Model("gemma2:9b", ollama_client),
)
creativity_expert = mar.Entity(
    "Creative Spark",
    "an expert in creativity and coming up with ideas",
    "",
    Model("llama3.1", ollama_client),  # Ollama
)
math_expert = mar.Entity(
    "Math Expert",
    "an expert in math and solving math problems",
    "",
    Model("qwen2.5:32b", ollama_client),  # Ollama
)
user = mar.Entity(
    "Competition Manager",
    "the manager of the competition",
    "",
    is_user=True,  # Prompts for stdin input when the user is sent a message
    pin_to_all_models=True,  # Lets all models see messages from this user.
)

for entity in mar.entities:
    entity.message_stack.append(
        Message(
            system,
            entity,
            f"This is the messaging application. Your team includes: {'\n'.join([f'{e.id}: {e.introduction[0].upper()+e.introduction[1:]}.' for e in mar.entities if e != entity])}. You may address messages to any of them and receive messages from any of them. You may not send messages to anyone outside of your team. Your messages are private; only the sender and receiver can see them. Thus, you will need to share information with your teammates. There can only be one recipient per message, the messaging application does not support sending messages to multiple recipients at once. You are {entity.id}, {entity.introduction}. {entity.personal_prompt + " " if entity.personal_prompt else ''}Messages sent by you are started with To: and messages sent to you are started with From:.",
        )
    )


mar.start(team_leader.send(input("You: "), user, print_all_messages=True))
