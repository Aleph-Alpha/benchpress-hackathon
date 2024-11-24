def generate_prompt(question, fn_name, fn_name_only,input_examples, output_examples):
    """
    Generates a robust prompt for code generation dynamically based on inputs.

    Args:
        problem_description (str): A detailed description of the problem.
        fn_name (str): Name of the function to be implemented.
        input_examples (list): A list of input example lists.
        output_examples (list): A list of corresponding output examples.

    Returns:
        str: A complete formatted prompt for the AI to generate Python code.
    """
    # Create the prompt dynamically
    test_data = generate_test_cases(input_examples, output_examples, fn_name_only)
    prompt = f"""


<|begin_of_text|><|start_header_id|>system<|end_header_id|>
System Prompt:
As an AI language model designed to generate robust and runnable Python code, your task is to:

- Understand the Problem: Carefully read the provided problem description, function definition, and input/output examples.
- Plan the Solution: Before coding, think through the logic, algorithms, or calculations required to solve the problem.
- Write the Code: Implement the solution as a Python function. The code should be correct, efficient, and adhere to best practices and support all needed input and output formats.
- Provide Output in XML Format: Output your response in an XML structure that separates the planning from the code, making it easy to parse. Use the specified format, ensuring the code is enclosed within <![CDATA[ ... ]]> tags.
- Ensure Code Runability: The code should be directly runnable as Python code and consist only of the function definition and its body, without any input/output operations.<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Please generate a Python function based on the following problem description, function definition, and input/output examples.
# Problem Description:

{question}

# Function Definition:

{fn_name}

## Input and Output Examples:

{test_data}

## Instructions:

Understand the Problem: Carefully read the problem description and analyze the input and output examples to fully understand what is required.

Plan Your Solution: Before coding, plan your approach to solving the problem. Outline the logic, algorithms, or calculations you will use.

Write the Code: Implement your solution as a Python function fully. Assume there are no previous implementations. The code should be robust, efficient, and adhere to best practices. Ensure that the all inputs types defined below in the Sample Test cases are suppoerted (e.g. integers, floats and strings).

Output Format: Provide your solution in an XML format that separates the planning from the code, making it easy to parse. Use the following structure:

<solution>
    <planning>
        Provide a detailed planning and explanation here. Describe the steps you will take to solve the problem, the algorithms or calculations used, and any special considerations.
    </planning>
    <code>
<![CDATA[
        # Your complete Python function code here
]]>
    </code>
</solution>
Important Notes:

The code shall consist of only the function definition and its body and include any necessary imports for the functions. Do not include any code for input/output (e.g., no print statements, no input prompts).
Use <![CDATA[ ... ]]> within the <code> tags to ensure that special characters are handled correctly in XML.
Ensure that the XML is well-formed and can be parsed without errors.
Example:

Suppose the problem is:

# Problem Description:

"Given two integers a and b, return their sum."

# Function Definition:

def add_numbers(a, b):

## Input and Output Examples:

Input: "[1, 2]"
Expected output: 3
Input: "[5, 7]"
Expected output: 12
Input: "[-1, -3]"
Expected output: -4

Your response should be:

<solution>
    <planning>
        To solve this problem, I need to create a function that takes two integers as input and returns their sum. I can simply use the `+` operator to add the two numbers.
    </planning>
    <code>
<![CDATA[
def add_numbers(a, b):
    return a + b
]]>
    </code>
</solution>
Important: Your response must be in XML format and contain the Python code inside <code> block to solve the problem defined above.<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

    return prompt

    
def generate_test_cases(inputs, outputs, fn_name_only):
    """
    Generates formatted test cases for inclusion in the prompt.

    Args:
        input_output (dict): A dictionary containing "inputs" and "outputs" keys with corresponding data.

    Returns:
        str: A string containing the formatted test cases.
    """
    # Ensure inputs and outputs have the same length
    if len(inputs) != len(outputs):
        raise ValueError("The number of inputs and outputs must match.")
    
    test_cases = "## Sample Test cases:\n"
    for i, (input_set, output_set) in enumerate(zip(inputs, outputs)):
        test_cases += f"{fn_name_only}{format_data_as_string(input_set)} --> Expected output: {output_set[0]}\n"
    
    return test_cases


def format_data_as_string(data):
    """
    Formats a list into a string where the entire list is wrapped in parentheses,
    preserving the structure and order of elements.
    
    Example:
    [[1, 2, 7], 3, 4] -> "([1, 2, 7], 3, 4)"
    [[1, 2, 7], 3] -> "([1, 2, 7], 3)"
    [[1, 2, 7], 3, [4, 5], 6] -> "([1, 2, 7], 3, [4, 5], 6)"
    
    :param data: A list of elements.
    :return: A formatted string.
    """
    if isinstance(data, list) and len(data) > 0:
        # Use tuple formatting to wrap the elements
        formatted = ", ".join(map(str, data))
        return f"({formatted})"
    else:
        raise ValueError("Input must be a non-empty list.")