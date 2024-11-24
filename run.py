import os
import time
import random
import argparse
from typing import List, Dict, Any
from aleph_alpha_client import Client, CompletionRequest, Prompt
from utilities import load_sample, run_test_cases, score
from utils import get_cot_prompt, get_sample_io_str
import prompting
import re
import xml.etree.ElementTree as ET
import multiprocessing

AA_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyNTk4OCwidG9rZW5faWQiOjY0MzB9.Pr0srrnvB4i34-Ml98SU4Avok7Ib-V6wv_T3E2Wm0jc"  # Replace with your actual token
MODEL = "llama-3.1-70b-instruct-long-context"

if not AA_TOKEN:
    raise ValueError("Aleph Alpha Playground token is not set. Please set the AA_TOKEN environment variable.")

def is_syntax_correct(code: str) -> bool:
    try:
        compile(code, '<string>', 'exec')
        return True, "Code executed successfully."
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except NameError as e:
        return False, f"NameError: {e}"
    except TypeError as e:
        return False, f"TypeError: {e}"
    except Exception as e:
        return False, f"Error: {type(e).__name__}: {e}"

def generate_single_code_solution(args):
    prompt, temperature = args
    # Create a new client in each process
    client = Client(AA_TOKEN)
    request = CompletionRequest(
        prompt=Prompt.from_text(prompt),
        maximum_tokens=10000,
        temperature=temperature,  # Adjusted temperature for diversity
        stop_sequences=[],
        echo=False
    )
    response = client.complete(request, model=MODEL)
    code_block_match = re.search(r"<code>.*?</code>", response.completions[0].completion.strip(), re.DOTALL)
    if code_block_match:
        code_block = code_block_match.group()
        # Parse the extracted XML block
        root = ET.fromstring(code_block)
        # Extract the code from within CDATA
        code = root.text.strip()
    else:
        print("No <code> block found in the text.")
        code = ""
    success, compile_text = is_syntax_correct(code)
    if success:
        return code
    else:
        # Optionally, attempt to debug the code
        # For now, return None
        print("Discarded code with syntax error.")
        return None

def generate_code_solutions(problem: dict, client: Client, num_samples: int, temperature: float, start_time: float, time_limit: float) -> List[str]:
    """
    Generate multiple code solutions for a given problem, ensuring they have correct syntax.

    Args:
        problem (dict): The problem to solve.
        client (Client): The Aleph Alpha client.
        num_samples (int): Number of code solutions to generate.
        temperature (float): Sampling temperature for diversity.
        start_time (float): Start time of the problem solving.
        time_limit (float): Maximum time allowed per problem in seconds.

    Returns:
        List[str]: A list of generated code solutions with correct syntax.
    """
    prompt = generate_code_prompt(problem)
    code_solutions = []
    attempts = 0
    max_attempts = num_samples * 2  # Allow up to twice the number of samples to account for syntax errors

    # Prepare arguments for multiprocessing
    pool_args = [(prompt, temperature) for _ in range(max_attempts)]
    
    with multiprocessing.Pool() as pool:
        for result in pool.imap_unordered(generate_single_code_solution, pool_args):
            # Check if we are close to the time limit
            elapsed_time = time.time() - start_time
            if elapsed_time >= time_limit - 10:  # Stop if less than 10 seconds remain
                print("Time limit approaching, returning best code solutions found so far.")
                break
            if result is not None:
                code_solutions.append(result)
                if len(code_solutions) >= num_samples:
                    break
            attempts += 1
            if attempts >= max_attempts:
                break

    if not code_solutions:
        # If no code solutions have correct syntax, return an empty list or handle accordingly
        print("No syntactically correct code solutions were generated.")
    return code_solutions

def generate_code_prompt(problem: dict) -> str:
    """
    Generate a prompt for code generation.

    Args:
        problem (dict): The problem to solve.

    Returns:
        str: The prompt for code generation.
    """
    return prompting.generate_prompt(
        problem['question'],
        problem['starter_code'],
        problem['input_output']['fn_name'],
        problem['input_output']['inputs'],
        problem['input_output']['outputs']
    )

def select_best_code_full(code_solutions: List[str], test_cases: List[Dict[str, Any]], problem: dict) -> str:
    """
    Select the best code solution by evaluating all code solutions on all test cases.

    Args:
        code_solutions (List[str]): List of generated code solutions.
        test_cases (List[Dict[str, Any]]): List of parsed test cases.
        problem (dict): The problem information.

    Returns:
        str: The selected code solution.
    """
    fn_name = test_cases[0]['fn_name'] if test_cases else ''
    code_solution_scores = []
    total_test_cases = len(test_cases)
    
    for code in code_solutions:
        # Prepare a problem dict with the test cases
        problem_with_test_cases = problem.copy()
        problem_with_test_cases['test_cases'] = {
            'fn_name': fn_name,
            'inputs': [tc['inputs'] for tc in test_cases],
            'outputs': [tc['outputs'] for tc in test_cases]
        }

        try:
            # Run test cases using the provided utility function
            test_results = run_test_cases(
                problem=problem_with_test_cases,
                generation=code,
                timeout=1
            )

            # Count the number of passed test cases
            num_passed = sum(1 for result in test_results if result['passed'])
            code_solution_scores.append((code, num_passed))
            # Early return if all test cases are passed
            if num_passed == total_test_cases:
                print("A code solution passed all test cases. Returning early.")
                return code


        except Exception as e:
            # If execution fails, consider zero passed tests
            code_solution_scores.append((code, 0))

    # Select the code solution with the highest number of passed test cases
    if not code_solution_scores:
        return code_solutions[0]  # Fallback

    best_code, _ = max(code_solution_scores, key=lambda x: x[1])
    return best_code

def generate_code_with_codet(problem: dict, client: Client, num_code_samples: int, temperature: float, time_limit: float = 300.0) -> str:
    """
    Generate code for a problem using the CODET method.

    Args:
        problem (dict): The problem to solve.
        client (Client): The Aleph Alpha client.
        num_code_samples (int): Number of code solutions to generate.
        temperature (float): Sampling temperature for diversity.
        time_limit (float): Maximum time allowed per problem in seconds (default 300 seconds).

    Returns:
        str: The selected code solution.
    """
    start_time = time.time()
    # Generate code solutions
    code_solutions = generate_code_solutions(problem, client, num_code_samples, temperature, start_time, time_limit)

    # Use existing test cases from 'input_output' only
    test_cases = []
    # From 'input_output'
    input_output = problem.get('input_output', {})
    inputs_list = input_output.get('inputs', [])
    outputs_list = input_output.get('outputs', [])
    fn_name = input_output.get('fn_name', problem.get('starter_code').split('(')[0].strip())
    for inputs, outputs in zip(inputs_list, outputs_list):
        test_cases.append({
            'inputs': inputs,
            'outputs': outputs,
            'fn_name': fn_name
        })

    if not test_cases:
        # If no valid test cases were available, return the first code solution
        return code_solutions[0] if code_solutions else ""

    # Evaluate code solutions on test cases from 'input_output' only
    best_code = select_best_code_full(code_solutions, test_cases, problem)

    return best_code

def main():
    parser = argparse.ArgumentParser(description='CODET Benchmark Script')
    parser.add_argument('--num_code_samples', type=int, default=20, help='Number of code samples to generate')
    parser.add_argument('--temperature', type=float, default=0.8, help='Sampling temperature for diversity')
    parser.add_argument('--length', type=int, default=100, help='Number of problems to evaluate')
    args = parser.parse_args()

    client = Client(AA_TOKEN)

    passed_problems, passed_test_cases = score(
        generation_func=lambda problem, client: generate_code_with_codet(
            problem,
            client,
            args.num_code_samples,
            args.temperature
        ),
        client=client,
        dataset_path="./data/val",  # Path to your validation set
        length=args.length,  # Adjust the number of problems to evaluate
    )
    print(f"Passed {passed_problems*100}% of problems")
    print(f"Passed {passed_test_cases*100}% of test cases")

if __name__ == "__main__":
    # Set the start method to 'spawn' to avoid OSError issues
    multiprocessing.set_start_method('spawn')
    main()
