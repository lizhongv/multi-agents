from glob import glob
import pandas as pd
import json
import time
import random
import openai

openai.api_base = 'https://api.closeai-asia.com/v1'
openai.api_key = 'sk-bA4N4H8xDy5uurP6y5o4EBXHi0ewyT3lzVvW2kepzKPtYDlP'


def construct_user_message(other_agents, idx_of_last_round_assistant_response):
    """construct user input"""
    if len(other_agents) == 0:
        self_check = "Can you double check that your answer is correct. Put your final answer in the form (X) at the end of your response."
        return {"role": "user", "content": self_check}
    else:
        prefix_string = "These are the solutions to the problem from other agents: "
        suffix_string = """\n\n Using the reasoning from other agents as additional advice, can you give an updated answer? Examine your solution and that other agents step by step. Put your answer in the form (X) at the end of your response."""  # .format(question)

        content = prefix_string
        for agent in other_agents:
            agent_last_response = agent[idx_of_last_round_assistant_response]["content"]
            check_response = "\n\n One agent solution: ```{}```".format(agent_last_response)
            content += check_response
        content += suffix_string

        return {"role": "user", "content": content}


def construct_assistant_message(content):
    return {"role": "assistant", "content": content}


def generate_answer(answer_context, model='gpt-3.5-turbo'):
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=answer_context,
            n=1)
    except:
        print("retrying due to an error......")
        time.sleep(20)
        return generate_answer(answer_context)

    response = completion["choices"][0]["message"]["content"]
    return response


def parse_question_answer(df, ix):
    question = df.iloc[ix, 0]
    a, b, c, d = df.iloc[ix, 1], df.iloc[ix, 2], df.iloc[ix, 3], df.iloc[ix, 4]

    question = "Can you answer the following question as accurately as possible? " \
               "{}: A) {}, B) {}, C) {}, D) {} " \
               "Explain your answer, putting the answer in the form (X) at the end of your response.".format(question, a, b, c, d)

    answer = df.iloc[ix, 5]

    return question, answer


if __name__ == "__main__":
    agents = 3
    rounds = 2

    data_dir = "/data0/lizhong/data/MMLU/test/*.csv"
    tasks = glob(data_dir)

    dfs = [pd.read_csv(task) for task in tasks]

    random.seed(0)
    response_dict = {}

    for i in range(5):
        df = random.choice(dfs)
        ix = len(df)
        idx = random.randint(0, ix - 1)

        question, answer = parse_question_answer(df, idx)

        message = {"role": "user", "content": question}
        all_agent_contexts = [[message] for agent in range(agents)]

        for round in range(rounds):
            for i, cur_agent_context in enumerate(all_agent_contexts):

                if round != 0:
                    other_agent_contexts = all_agent_contexts[:i] + all_agent_contexts[i + 1:]  # all except agent i
                    user_message = construct_user_message(other_agent_contexts, 2 * round - 1)
                    cur_agent_context.append(user_message)

                response = generate_answer(cur_agent_context, model='gpt-3.5-turbo')
                print(response)

                assistant_message = construct_assistant_message(response)
                cur_agent_context.append(assistant_message)

        response_dict[question] = (all_agent_contexts, answer)

    json.dump(response_dict, open("mmlu_{}_{}.json".format(agents, rounds), "w"), indent=2)
