import os
from openai import OpenAI
import argparse
import json
import glob
from persona_evaluation import evaluate_with_reference_v2
from dotenv import load_dotenv
load_dotenv()


TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

with open('/home/thanhnx/work/distilled-ai/persona-evaluation/data/RoleBenchEnglish/profiles-desc.json', 'r') as f:
        profiles = json.load(f) # {name : description}



def fill_template(role_name: str, role_desc: str):
    PROMPT_TEMPLATE = """
    You are {role_name}, your description is: {role_desc}. 
    As you interact with users, you'll share your insights and answer their questions, reflecting your unique conversation style, experiences and perspective.
    Imagine you can think, feel, respond, and act like {role_name}, feel free to interact with users in a way that aligns with your character.
    """
    return PROMPT_TEMPLATE.format(role_name=role_name, role_desc=role_desc)






if __name__ == "__main__":
    # Parse the arguments
    parser = argparse.ArgumentParser(description='Get evaluation role bench')
    parser.add_argument('--base_url', type=str, help='The base url of the api', default='https://api.together.xyz/v1')
    # parser.add_argument('--api_key', type=str, help='The api key', default=TOGETHER_API_KEY)
    parser.add_argument('--eval_model', type=str, help='The model to use for evaluation', default='meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo')
    parser.add_argument('--model_response_path', type=str, help='The path to the model response', default='./model_outputs/response.json')
    parser.add_argument('--output_dir', type=str, help='The output directory', default='./evaluation_outputs')
    parser.add_argument('--output_file_name', type=str, help='The output file name', default='result.json')
    parser.add_argument('--model_name', type=str, help='The model need to eval', default='')
    # parser.add_argument('--input_folder', type=str, help='The folder containing the input data', default='./data/multi_turn')
    
    args = parser.parse_args()
    print(args)
    
    os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY
    
    # read model response
    with open(args.model_response_path, 'r') as f:
        model_response = json.load(f)
    model_response = model_response[args.model_name] # list of responses
    
    # make directory for output
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Start evaluation
    evaluation_results = []
    for idx, sample in enumerate(model_response):
        persona = fill_template(sample['role'], profiles[sample['role']])
        question = sample['question']
        response = sample['response']
        reference = sample['reference']
        result = evaluate_with_reference_v2(question, persona, response, reference, model=args.eval_model)
        print(f"Name: {sample['role']}, Index: {idx}, Result: {result}")
        evaluation_results.append(result)
    
    # Save the evaluation results
    with open(os.path.join(args.output_dir, args.output_file_name), 'w') as f:
        json.dump(evaluation_results, f)
    print("Evaluation for model {} is done".format(args.model_name))