import json
import openai
import numpy as np
import time
import re

def parse_bullets(sentence):
    bullets_preprocess = sentence.split("\n")
    bullets = []

    for bullet in bullets_preprocess:
        try:
            idx = bullet.find(next(filter(str.isalpha, bullet)))
        except:
            continue

        bullet = bullet[idx:]

        if len(bullet) != 0:
            bullets.append(bullet)

    return bullets


def parse_yes_no(string):
    """
    Parses a string containing "yes" or "no" and returns a boolean value.

    Args:
        string (str): The string to parse.

    Returns:
        bool: True if the string contains "yes", False if the string contains "no".

    Raises:
        ValueError: If the input string does not contain "yes" or "no".
    """
    if "yes" in string.lower():
        return True
    elif "no" in string.lower():
        return False
    else:
        return None


def solve_math_problems(input_str):
    """return float"""
    pattern = r"\d+\.?\d*"

    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1]

    return None

def parse_answer(input_str):
    # pattern = r'\((\w)\)'
    pattern = r'\(([A-D])\)'
    matches = re.findall(pattern, input_str)

    solution = None
    for match_str in matches[::-1]:
        solution = match_str.upper()
        if solution and solution in ['A', 'B', 'C', 'D']:
            break

    return solution

def compute_accuracy(gt, pred_solutions):
    if type(pred_solutions) == list:
        pred_answers = []
        for pred_solution in pred_solutions:
            pred_answer = parse_answer(pred_solution) # A, B, C, D or None
            if pred_answer is not None:
                pred_answers.append(pred_answer)
            # if pred_answer is None:
            #     pred_answer = solve_math_problems(pred_solution)

        if len(pred_answers):
            final_answer = most_frequent_answer(pred_answers)
             # pred_answer = pred_answers[0]
        else:
            return 0
    else:
        pred_answer = parse_answer(pred_solutions)
        if pred_answer is not None:
            final_answer = pred_answer
        # if pred_answer is None:
        #     pred_answer = solve_math_problems(pred_solutions)
        else:
            return 0


    if gt == final_answer:
        return 1
    else:
        return 0


def most_frequent_answer(answers_list):
    """return A,B,C,D"""
    max_cnt = 0
    final_answer = ""

    for answer in answers_list:
        current_frequency = answers_list.count(answer)
        if current_frequency > max_cnt:
            max_cnt = current_frequency
            final_answer = answer

    return final_answer

if __name__ == "__main__":
    response_dict = json.load(open("mmlu_3_2.json", "r"))
    all_questions = list(response_dict.keys())

    accuracies = []
    for q in all_questions:
        diff_agent_responses, ground_truth = response_dict[q]

        pred_solutions = []  # different agents give answers to the same question
        for response in diff_agent_responses:
            pred_solution = response[-1]['content']
            pred_solutions.append(pred_solution)
            # break

        # pred_solutions = pred_solutions[:1]
        accurate = compute_accuracy(ground_truth, pred_solutions)


        if accurate is not None:
            accuracies.append(float(accurate))
        else:
            import pdb
            pdb.set_trace()
            print(ground_truth)

    print("accuracies:", np.mean(accuracies), np.std(accuracies) / (len(accuracies) ** 0.5))