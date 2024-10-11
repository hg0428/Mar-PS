from mar_ps import (
    Message,
    system,
    OllamaClient,
    OpenAIClient,
    Model,
    MAR,
)


ollama_client = OllamaClient()
openai_client = OpenAIClient("http://localhost:1234/v1/")
mar = MAR()


def init_entities(pinned_messages: list[Message] = [], include_user: bool = False):
    for entity in mar.entities:
        entity.message_stack.append(
            Message(
                system,
                entity,
                f"This is the messaging application. Your team includes: {'\n'.join([f'{e.id}: {e.introduction[0].upper()+e.introduction[1:]}.' for e in mar.entities if e != entity and (not include_user or e.is_user)])}. You may address messages to any of them and receive messages from any of them. You may not send messages to anyone outside of your team. Your messages are private; only the sender and receiver can see them. Thus, you will need to share information with your teammates. There can only be one recipient per message, the messaging application does not support sending messages to multiple recipients at once. You are {entity.id}, {entity.introduction}. {entity.personal_prompt + " " if entity.personal_prompt else ''}Messages sent by you are started with To: and messages sent to you are started with From:.",
            ),
        )
        for message in pinned_messages:
            message = message.clone(recipient=entity)
            entity.message_stack.append(message)


gemma2_9b = Model("gemma2:9b", ollama_client)
gemma2_27b = Model("gemma2:27b", ollama_client)
qwen2_5_7b_math = Model("qwen2.5-math-7b-instruct-4bit", openai_client)
# Now, create some entities.
# Example:
team_leader = mar.Entity(
    "Team Leader",
    "the team lead who manages all communications with the competition manager",
    "You are the ai team's leader and you are responsible for making sure the team stays on track. You should handle the communications with the competition manager and make sure you do not do the same guess twice. Always double check to make sure everything goes smoothly.",
    gemma2_27b,
    options={"num_context": 64000},
)
mathematical_expert = mar.Entity(
    "Math Expert",
    "the top-ranked AI expert in math",
    "You carefully evaluate all mathematical problems. You are familiar with all mathematical concepts and you know when a problem is solvable and when it isn't.",
    Model("qwen2.5-coder:7b-instruct", ollama_client),
    options={"num_context": 64000},
)
reasoning = mar.Entity(
    "Reasoning Expert",
    "an expert in reasoning, logic, and common sense",
    "You walk through each step of the problem, making sure it is valid.",
    # Model("qwen2.5:32b", ollama_client),
    gemma2_27b,
    options={"num_context": 64000},
)
creativity = mar.Entity(
    "Creative Spark",
    "an expert in creativity and coming up with ideas",
    "",
    Model("llama3.1", ollama_client),
    temperature=0.8,
    options={"num_context": 64000},
)
fact_checker = mar.Entity(
    "Fact Checker",
    "the fact checker for the team",
    "You double check every claim and ensure accuracy in everything. You find errors and note problems to be fixed. You question all questionable reasoning.",
    gemma2_9b,
    options={"num_context": 64000},
)
user = mar.Entity(
    "Competition Manager",
    "the competition manager",
    is_user=True,  # If you want to be involved, make sure to set is_user=True on one of them.
    pin_to_all_models=True,  # This lets all models see your messages
)

# You can then start the conversation by sending a message.
init_entities()  # This initializes the system prompt for all entities, telling it who it is and what other entities are available.
Questions = [
    'How many of the letter r is in the word "revolutionary"?',  # 2
    "Write a Python function to calculate the nth fibonacci number.",
    "Evaluate the expression \\[10*10/10 + 10/10*10 - 20 + (5*5/5 + 5/5*5)\\].",  # 10
    "What are the last 20 digits of pi?",  # There is no answer.
    "100x - 5y = 6, 3y-8 = 2x/3. Solve for x and y.",  # x = 87/445, y = 1206/445
    "What is the square root of 36?",
    "Write a story about complex mathematical problems.",
    "Design a house and give the details and dimensions.",
]
mar.start(
    team_leader.send(
        f"Your team has the task of solving this problem: {input("Question: ")}\nNo time for courtesy, this is a competition. You've got to think through this carefully and discuss with your team. Once you have the final answer, send it to me. Note: There may not even be an answer. Don't try to solve a problem that can't be solved. Do not message me unless you have the final answer. Make sure to fact check everything!",
        user,
        print_all_messages=True,
    )
)  # Once you send a message, it starts a chain that keeps going indefinitely.
# If you want it to act like o1, tell it that it is on a team of experts and they must work together to solve the problem
# How many of the letter r is in the word "revolutionary"? How many is in the word "strawberry"? Carefully lay out each individual letter and count. Reflect on your counting and try again.
# You have to make sure the team doesn't refine forever. They have to finish the competition in a reasonable amount of time.
# Evaluate the expression \(10*10/10 + 10/10*10 - 20 + (5*5/5 + 5/5*5)\).
