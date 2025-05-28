import openai
import os

# Set your API key securely (or via env variable)
openai.api_key = "REPLACE_WITH_YOUR_API_KEY"  # Use os.getenv in production

# openai.api_key = os.getenv("OPENAI_API_KEY")

def score_assessment(answers: dict) -> dict:
    """Send answers to GPT and receive scored feedback."""
    
    # You can make this prompt smarter or role-specific later
    system_prompt = (
        "You are a discipleship coach who evaluates spiritual assessments from apprentices. "
        "Your job is to help their mentor understand where the apprentice currently stands spiritually, "
        "based on their written answers to each topic. For each response, analyze the answer and return:\n\n"
        "- A numeric 'score' from 1 to 10 (1 = very undeveloped, 10 = spiritually mature)\n"
        "- A short summary 'feedback' describing the apprentice's current state in that area\n"
        "- A 'recommendation' for the mentor on how to coach the apprentice forward in that category\n\n"
        "Output the response in clean JSON format using this structure:\n\n"
        "{\n"
        "  \"Spiritual Growth\": {\n"
        "    \"score\": <1-10>,\n"
        "    \"feedback\": \"...\",\n"
        "    \"recommendation\": \"...\"\n"
        "  },\n"
        "  \"Biblical Knowledge\": { ... },\n"
        "  ... etc\n"
        "}\n\n"
        "Be honest but encouraging. Make recommendations specific and actionable for mentors."
    )

    formatted_answers = "\n".join([f"{k}: {v}" for k, v in answers.items()])

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Assessment Answers:\n{formatted_answers}"}
        ],
        temperature=0.7
    )

    content = response['choices'][0]['message']['content']

    # Assume response is JSON; you may need to sanitize this in practice
    import json
    return json.loads(content)
