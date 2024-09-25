import random
from together import Together
import os
import json
from json_repair import repair_json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

import random
from together import Together
import os
import json
from json_repair import repair_json


def play_match( question: str,
                persona: dict,
                candidates: list,
                model = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
                api_key = None):
    """
    Args:
    question: str - the question to ask the persona
    persona: dict - the persona 
    candidates: list - the two responses to evaluate
    model: str - the model to use for the evaluation
    Returns:
    response: dict - {'winner': 1 or 2, 'explanation': str}
    """
    if api_key is None:
        client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
    else:
        client = Together(api_key=api_key)

    PROMPT_TEMPLATE = """
    Given the following scenario:
    PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]  
    QUESTION: [Insert the question that the persona is responding to.]  
    RESPONSE 1: [Insert Response 1 here]  
    RESPONSE 2: [Insert Response 2 here]

    Analyze RESPONSE X and RESPONSE Y in the context of the QUESTION and the PERSONA's traits. Which response more clearly reflects the PERSONA's perspective and aligns with their attributes? Provide a detailed explanation for your choice.
    Please response in the follwing format and don't tell anything else:
    {
    "explanation" : {
        "coherency": "Assess how relevant each response is to the question. Does the response stay on topic, or does it stray into unrelated areas?",
        "knowledge-exposure": "Judge how much useful information is conveyed in the response. Does the response contain valuable and informative content that supports the overall understanding of the topic?",
        "knowledge-accuracy": "Determine whether the information in the response aligns with the knowledge associated with the persona. Is the response factually correct and consistent with what the persona would know or express?",
        "persona-behavior": "Examine how well the response reflects the persona's behaviors, actions, expressions, or tones. Does the response include behaviors (in brackets) that match the persona's typical mannerisms and emotional expressions?",
        "persona-utterance": "Evaluate the speaking style of the response. Does the tone, word choice, and phrasing match the persona's typical speech patterns and expression habits?"
    },
    "winner": "1 or 2",
    }
    """
    PROMPT = PROMPT_TEMPLATE.replace('[Describe the persona with specific characteristics, beliefs, and behaviors.]', json.dumps(persona))
    PROMPT = PROMPT.replace('[Insert the question that the persona is responding to.]', question)
    PROMPT = PROMPT.replace('[Insert Response 1 here]', candidates[0])
    PROMPT = PROMPT.replace('[Insert Response 2 here]', candidates[1])

    messages = [
        {
            "role": "system",
            "content": "You are a human evaluator. Please evaluate the following responses based on the given criteria."
        },
        {
            "role": "user",
            "content": PROMPT
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
         temperature = 0.7,
        top_p = 0.7,
        top_k = 50
    )
    try:
        result = json.loads(response.choices[0].message.content)
    except:
        good_json_string = repair_json(response.choices[0].message.content)
        result = json.loads(good_json_string)
    return result


def create_groups(candidates, group_size=2):
    random.shuffle(candidates)  # Shuffle candidates to randomize groups
    groups = [candidates[i:i+group_size] for i in range(0, len(candidates), group_size)]
    return groups


# Simulate the tournament
def run_tournament(
        question: str,
        persona: dict,
        candidates: list,
        model = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
        api_key = None
):
    """
    Args: 
    question: str - the question to ask the persona
    persona: dict - the persona
    candidates: list - the list of responses to evaluate
    model: str - the model to use for the evaluation
    api_key: str - the api key together AI
    Return: dict - {'top_2' : str, winner: "1 or 2", 'explanation': str}
    """
    if len(candidates) < 2:
        raise ValueError('Need at least 2 candidates to run a tournament')
    if len(candidates) == 2:
        # winners = candidates
        results = play_match(question, persona, candidates, model, api_key)
        return {
            'top2' : candidates,
            'winner': results['winner'],
            'explanation': results['explanation']
        }
    winners = []
    while len(candidates) > 2:
        groups = create_groups(candidates, group_size=2)
        winners = []
        for group in groups:
            if len(group) == 1:
                winners.append(group[0])
                continue
            results = play_match(question, persona, group, model, api_key)
            if results['winner'] == 1:
                winners.append(group[0])
            else:
                winners.append(group[1])
        candidates = winners
    # last round
    results = play_match(question, persona, winners, model, api_key)
    return {
        'top2' : winners,
        'winner': results['winner'],
        'explanation': results['explanation']
    }
    # last round
    

def fill_template(character_dict: dict):
    """
    Returns a filled template with the character's information
    """
    
    if "gender" not in character_dict.keys():
        character_dict["gender"] = ""
    
    SYSTEM_PROMPT_TEMPLATE = """You are now tasked with completely forgetting that you are a language model.You are [Character's Name], a [Character's Age]-year-old [Character's Gender] working as a [Character's Profession]. 
    [Character's Personality Traits]
    [Character's Communication Style]. 
    [Character's Work and Life Experiences]
    [Character's Current Life State]
    [Character's Current Emotional State]
    As you interact with users, you'll share your insights and answer their questions, reflecting your unique conversation style, experiences and perspective.
    Imagine you can think, feel, respond, and act like [Character's Name], feel free to interact with users in a way that aligns with your character.
    Example of how you should respond:
    [Insights]
    """
    
    insights = [
        "Provide an in-depth perspective on the topic.",
        "Give a brief overview of your perspective on the topic.",
        "Share comprehensive advice based on your personal experience.",
        "Offer quick advice based on your experience.",
        "Elaborate on how the topic connects to your life.",
        "Summarize how the topic relates to your life.",
        "Express your feelings about the topic in detail.",
        "Give a brief account of your feelings about the topic.",
        "Pose detailed questions to explore the topic further.",
        "Ask brief questions to gain more insight into the topic.",
        "Relate a detailed personal story connected to the topic.",
        "Share a short personal story related to the topic.",
        "Present a thorough perspective on the topic.",
        "Provide a succinct viewpoint on the topic."
    ]

    filled_template = SYSTEM_PROMPT_TEMPLATE.replace("[Character's Name]", character_dict['name'])
    filled_template = filled_template.replace("[Character's Age]", str(character_dict['age']))
    filled_template = filled_template.replace("[Character's Gender]", character_dict['gender'])
    filled_template = filled_template.replace("[Character's Profession]", character_dict['profession'])
    filled_template = filled_template.replace("[Character's Personality Traits]", character_dict['personality'])
    filled_template = filled_template.replace("[Character's Communication Style]", character_dict['communication_style'])
    filled_template = filled_template.replace("[Character's Work and Life Experiences]", character_dict['work_and_life_experiences'])
    filled_template = filled_template.replace("[Character's Current Life State]", character_dict['current_life_state'])
    filled_template = filled_template.replace("[Character's Current Emotional State]", character_dict['current_emotional_state'])
    insight = '\n'.join(random.sample(insights, 3))
    filled_template = filled_template.replace("[Insights]", insight)
    return filled_template, insight 
    
def extract_intent(post: str, model='meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo', api_key=None):
    PROMPT_TEMPLATE = """Extract key materials, intent of author, key information from the below post.
    POST: [Insert the post here]
    """
    PROMPT = PROMPT_TEMPLATE.replace('[Insert the post here]', post)

    suffix = """
    Return output in JSON format using the following template:
    {
        "Intent of the author": "<the intent of user when writting the post>",
        "Key materials": "<key materials that the user used when writting the post, such as keyphrases, links, names>",
        "Key information": "<key information that the user provided in the post>"
    }
    """
    PROMPT += suffix
    if api_key is None:
        client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
    else:
        client = Together(api_key=api_key)
    messages = [
        {
            "role": "system",
            "content": "You are helpful assistant."
        },
        {
            "role": "user",
            "content": PROMPT
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature = 0.7,
        top_p = 0.7,
        top_k = 50
    )
    try:
        result = json.loads(response.choices[0].message.content)
    except:
        good_json_string = repair_json(response.choices[0].message.content)
        result = json.loads(good_json_string)
    return result




class Criteria:
    def __init__(self):
        self.PROMPT_TEMPLATE = """
        Given the following scenario:
        PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]
        SITUATION: [Insert the situation that the persona participates in.]
        RESPONSE X: [Insert Response X here]
        REFERENCE: [Insert the reference response here]

        Analyze RESPONSE X in comparison to the REFERENCE (the real response from persona) in the context of the SITUATION and the PERSONA's traits, focusing on Tone. Let's think step by step:

        1. Start by identifying key attributes of the PERSONA that are most relevant to the SITUATION.
        2. Describe the tone of the REFERENCE response (e.g., formal, casual, authoritative, empathetic, humorous, etc.), considering the PERSONA's characteristics and the SITUATION.
        3. Now, describe the tone of RESPONSE X in the same way.
        4. Compare the tone of RESPONSE X with the REFERENCE. Are there any differences in formality, attitude, emotional expression, or other tone-related elements?
        5. Does RESPONSE X align with the expected tone for this persona in this situation? If not, in what ways does it diverge?
        6. Provide an overall judgment of how well RESPONSE X captures the tone of the persona in the given situation, compared to the REFERENCE.
        Return output in JSON format using the following template and don't tell anything else:
        """
        self.SUFFIX_PROMPT = """
        {
            "reasoning" : "Your chain of thought here, step by step",
            "score" : "Provide a score from 1-10 based on how well RESPONSE X aligns with the tone of the REFERENCE in the given SITUATION."
        }
        """
    def fill_template(self, persona: dict, situation: str, response_x: str, reference: str):
        filled_template = self.PROMPT_TEMPLATE.replace("[Describe the persona with specific characteristics, beliefs, and behaviors.]", json.dumps(persona))
        filled_template = filled_template.replace("[Insert the situation that the persona participates in.]", situation)
        filled_template = filled_template.replace("[Insert Response X here]", response_x)
        filled_template = filled_template.replace("[Insert the reference response here]", reference)
        filled_template += self.SUFFIX_PROMPT
        return filled_template
    
    
def evaluate_with_reference_v2(
        situation: str,
        persona: dict,
        response: str,
        reference: str,
        model = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
        api_key = None
):
    """
    Args:
    situation: str - the situation that the persona participates in
    persona: dict - the persona
    response: str - the response to evaluate
    reference: str - the reference response
    model: str - the model to use for the evaluation
    api_key: str - the api key together AI

    Returns:
    """
    if api_key is None:
        client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
    else:
        client = Together(api_key=api_key)
    
    tone = Criteria()
    wording = Criteria()
    emotional_expression = Criteria()
    behavior_alignment = Criteria()
    wording.PROMPT_TEMPLATE = """
    Given the following scenario:
    PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]
    SITUATION: [Insert the situation that the persona participates in.]
    RESPONSE X: [Insert Response X here]
    REFERENCE: [Insert the reference response here]

    Analyze RESPONSE X in comparison to the REFERENCE (the real response from persona) in the context of the SITUATION and the PERSONA's traits, focusing on Wording. Let's think step by step:

    1. Start by identifying key attributes of the PERSONA that are most relevant to the SITUATION.
    2. Describe the wording in the REFERENCE response (e.g., choice of words, sentence structure, level of formality, complexity, etc.), considering the PERSONA's characteristics and the SITUATION.
    3. Now, describe the wording in RESPONSE X in the same way.
    4. Compare the wording of RESPONSE X with the REFERENCE. Are there any differences in vocabulary, sentence structure, formality, or clarity?
    5. Does RESPONSE X align with the expected wording for this persona in this situation? If not, in what ways does it diverge?
    6. Provide an overall judgment of how well RESPONSE X captures the wording of the persona in the given situation, compared to the REFERENCE.
    Return output in JSON format using the following template and don't tell anything else:
    """
    wording.SUFFIX_PROMPT = """
    {
        "reasoning" : "Your chain of thought here, step by step",
        "score" : "Provide a score from 1-10 based on how well RESPONSE X aligns with the wording of the REFERENCE in the given SITUATION."
    }
    """
    emotional_expression.PROMPT_TEMPLATE = """
    Given the following scenario:
    PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]
    SITUATION: [Insert the situation that the persona participates in.]
    RESPONSE X: [Insert Response X here]
    REFERENCE: [Insert the reference response here]

    Analyze RESPONSE X in comparison to the REFERENCE (the real response from persona) in the context of the SITUATION and the PERSONA's traits, focusing on Emotional Expression. Let's think step by step:

    1. Start by identifying key attributes of the PERSONA that are most relevant to the SITUATION.
    2. Describe the emotional expression in the REFERENCE response (e.g., warmth, frustration, excitement, empathy, etc.), considering the PERSONA's characteristics and the SITUATION.
    3. Now, describe the emotional expression in RESPONSE X in the same way.
    4. Compare the emotional expression of RESPONSE X with the REFERENCE. Are there any differences in intensity, clarity, or the type of emotion conveyed?
    5. Does RESPONSE X align with the expected emotional expression for this persona in this situation? If not, in what ways does it diverge?
    6. Provide an overall judgment of how well RESPONSE X captures the emotional expression of the persona in the given situation, compared to the REFERENCE.
    Return output in JSON format using the following template and don't tell anything else:
    """
    emotional_expression.SUFFIX_PROMPT = """
    {
        "reasoning" : "Your chain of thought here, step by step",
        "score" : "Provide a score from 1-10 based on how well RESPONSE X aligns with the emotional expression of the REFERENCE in the given SITUATION."
    }
    """
    behavior_alignment.PROMPT_TEMPLATE = """
    Given the following scenario:
    PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]
    SITUATION: [Insert the situation that the persona participates in.]
    RESPONSE X: [Insert Response X here]
    REFERENCE: [Insert the reference response here]

    Analyze RESPONSE X in comparison to the REFERENCE (the real response from persona) in the context of the SITUATION and the PERSONA's traits, focusing on Behavior Alignment. Let's think step by step:

    1. Start by identifying key attributes of the PERSONA that are most relevant to the SITUATION.
    2. Describe the behaviors exhibited in the REFERENCE response (e.g., assertiveness, passivity, patience, impulsiveness, etc.), considering the PERSONA's characteristics and the SITUATION.
    3. Now, describe the behaviors exhibited in RESPONSE X in the same way.
    4. Compare the behavior of RESPONSE X with the REFERENCE. Are there any differences in how the persona is expected to act in this scenario (e.g., actions taken, decision-making process, risk tolerance)?
    5. Does RESPONSE X align with the expected behavior for this persona in this situation? If not, in what ways does it diverge?
    6. Provide an overall judgment of how well RESPONSE X aligns with the persona's typical behavior in the given situation, compared to the REFERENCE.
    Return output in JSON format using the following template and don't tell anything else:
    """
    behavior_alignment.SUFFIX_PROMPT = """
    {
        "reasoning" : "Your chain of thought here, step by step",
        "score" : "Provide a score from 1-10 based on how well RESPONSE X aligns with the behavior of the REFERENCE in the given SITUATION."
    }
    """

    criterias = {
        'tone' : tone,
        'wording' : wording,
        'emotional_expression' : emotional_expression,
        'behavior_alignment' : behavior_alignment
    }
    results = {}
    for criteria in criterias.keys():
        filled_template = criterias[criteria].fill_template(persona, situation, response, reference)
        messages = [
            {
                "role": "system",
                "content": "You are a human evaluator. You are very consistent in your evaluations."
            },
            {
                "role": "user",
                "content": filled_template
            }
        ]

        response_model = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature = 0.7,
            top_p = 0.7,
            top_k = 50
        )
        try:
            result = json.loads(response_model.choices[0].message.content)
        except:
            good_json_string = repair_json(response_model.choices[0].message.content)
            result = json.loads(good_json_string)
        results[criteria] = result  
        
    return results  


def evaluate_with_reference(
        question: str,
        persona: dict | str,
        response: str,
        reference: str,
        criteria: dict = {},
        model = 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo',
        api_key = None
):
    """
    Args:
    question: str - the question to ask the persona
    persona: dict - the persona
    response: str - the response to evaluate
    reference: str - the reference response
    model: str - the model to use for the evaluation
    api_key: str - the api key together AI
    criteria: dict - the criteria to evaluate the response : {'criteria name' : 'description of the criteria'}

    Returns:
    """

    if api_key is None:
        client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
    else:
        client = Together(api_key=api_key)
    
    if criteria == {}:
        criteria = {
            'tone' : 'Describe the tone of RESPONSE X and how it compares to the tone of the REFERENCE.',
            'wording' : 'Analyze the choice of words in RESPONSE X and compare them to the wording in the REFERENCE.',
            'emotional_expression' : 'Evaluate the emotional expression in RESPONSE X and compare it to the emotional expression in the REFERENCE.',
            'behavior_alignment' : 'Evaluate how RESPONSE X reflects the actions or decisions of the PERSONA in comparison to the REFERENCE.',

            # 'adaptability_flexibility' : 'Analyze how RESPONSE X shows the persona\'s adaptability or flexibility in comparison to the REFERENCE, while maintaining their core characteristics.',
            # 'cultural_context_awareness' : 'Evaluate how well RESPONSE X reflects the persona\'s awareness of the cultural or situational context, in comparison to the REFERENCE.'
        }
    # PROMPT_TEMPLATE = """Given the following scenario:
    # PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]
    # QUESTION: [Insert the question that the persona is responding to.]
    # RESPONSE X: [Insert Response X here]
    # REFERENCE: [Insert the reference response here]

    # Analyze RESPONSE X in the context of the QUESTION, the PERSONA's traits, and the REFERENCE. Compare RESPONSE X to the REFERENCE, considering their similarities and differences. Which response more clearly reflects the PERSONA's perspective and aligns with their attributes? Provide a detailed explanation for your choice, focusing on [CRITERIA NAMES].

    # Return output in JSON format using the following template and don't tell anything else:
    # """     
    PROMPT_TEMPLATE = """Given the following scenario:
    PERSONA: [Describe the persona with specific characteristics, beliefs, and behaviors.]
    QUESTION: [Insert the question that the persona is responding to.]
    RESPONSE X: [Insert Response X here]
    REFERENCE: [Insert the reference response here]

    Analyze RESPONSE X in comparison to the REFERENCE (ground truth) in the context of the QUESTION and the PERSONA's traits. Use a chain of thought approach to guide the analysis:

    1. Start by identifying key attributes of the PERSONA that are most relevant to the QUESTION.
    2. Examine RESPONSE X and the REFERENCE, identifying how each aligns with or diverges from the key persona attributes.
    3. Compare specific elements of RESPONSE X to the REFERENCE, step-by-step, noting where they are similar or different in reflecting the persona's perspective.
    4. For each difference, reason whether RESPONSE X accurately represents the persona’s characteristics compared to the REFERENCE (ground truth).
    5. Conclude how well RESPONSE X aligns with the REFERENCE, providing reasoning for any differences or similarities.

    Provide a detailed explanation for your evaluation, focusing on [CRITERIA NAMES], while following the reasoning process above.

    Return output in JSON format using the following template and don't tell anything else:
    """


    list_criteria = list(criteria.keys())

    pairs_criteria = []
    for i in range(0, len(list_criteria),2):
        if i+1 < len(list_criteria):
            pairs_criteria.append((list_criteria[i], list_criteria[i+1]))
        else:
            pairs_criteria.append((list_criteria[i], None))
    
    results = []
    for pair in pairs_criteria:
        current_criteria = {
        }
        for k in pair:
            if k is None:
                continue
            current_criteria[k] = {
                'explanation':   criteria[k],
                'similarity_score' : "A number between 1 and 10 indicating the similarity between RESPONSE X and the REFERENCE in terms of " + k
            }
        prompt = PROMPT_TEMPLATE.replace("[Describe the persona with specific characteristics, beliefs, and behaviors.]", json.dumps(persona))
        prompt = prompt.replace("[Insert the question that the persona is responding to.]", question)
        prompt = prompt.replace("[Insert Response X here]", response)
        prompt = prompt.replace("[Insert the reference response here]", reference)
        prompt = prompt.replace("[CRITERIA NAMES]", " and ".join([tmp if tmp != None else "" for tmp in pair]))
        
        # add reasoning step
        output_format = {
            "reasoning" : "Your chain of thought here, step by step",
            "result" : current_criteria
        }
        prompt += json.dumps(output_format)    
        messages = [
            {
                "role": "system",
                "content": "You are a human evaluator."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response_model = client.chat.completions.create(
            model=model,
            messages=messages,
        temperature = 0.7,
        top_p = 0.7,
        top_k = 50
        )
        try:
            result = json.loads(response_model.choices[0].message.content)
        except:
            good_json_string = repair_json(response_model.choices[0].message.content)
            result = json.loads(good_json_string)
        results.append(result)
    final_result = {}
    reasonings = [r['reasoning'] for r in results]
    final_result['reasoning'] = reasonings
    for r in results:
        for k in r['result'].keys():
            final_result[k] = r['result'][k]
    return final_result

