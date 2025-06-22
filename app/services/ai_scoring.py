from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def score_assessment(answers: dict) -> dict:
    """Send answers to GPT and receive scored feedback."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a discipleship coach who evaluates spiritual assessments from apprentices. "
                "Your job is to help their mentor understand where the apprentice currently stands spiritually, "
                "based on their written answers to each topic. For each response, analyze the answer and return:\n\n"
                "- A numeric 'score' from 1 to 10 (1 = very undeveloped, 10 = spiritually mature)\n"
                "- A short summary 'feedback' describing the apprentice's current state in that area\n"
                "- A 'recommendation' for the mentor on how to coach the apprentice forward in that category\n\n"
                "Output the response in clean JSON format using this structure:\n\n"
                "{\"q1\": {\"score\": 7, \"feedback\": \"...\", \"recommendation\": \"...\"}, ...}"
            )
        },
        {
            "role": "user",
            "content": "Assessment Answers:\n" + "\n".join([f"{k}: {v}" for k, v in answers.items()])
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
