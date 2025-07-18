import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.react_agent import graph

import pytest
import asyncio
from langsmith import unit
from react_agent import graph


system_prompt = """
You are a UI generation system. Given a task specification in YAML format, generate an interactive HTML interface that:

1. Displays a list of input texts and the predicted emotions.
2. Shows prediction details for each text including:
   - The original input text.
   - The predicted emotion label.
   - The probabilities of all emotion labels.
   - An emoji representing the predicted emotion.
3. Allows the user to input a new text passage and send it to the model API.
4. Displays the model's prediction for the new input (including probabilities and emoji).
"""

task_yaml = """
task_description:
  type: Text classification
  description: |
    Given a text passage authored by a person, this task aims to identify the underlying emotion expressed in the text. 
    The model classifies the emotion into one of the following categories: anger, disgust, fear, joy, neutral, sadness, or surprise. 
    The classification is based solely on the semantic and emotional cues present in the input text.
  input: |
    A single text passage written by an individual. The text may express an emotional state either explicitly (e.g., "I am so happy today!") or implicitly (e.g., "The sun finally came out after days of rain."). 
    The passage should be in natural language and may vary in length.

  output: |
    A single emotion label representing the primary emotion conveyed by the author in the text. 
    The possible labels are one of the following: anger, disgust, fear, joy, neutral, sadness, or surprise.

  visualize:
    description: |
      Display a list of input data along with the predicted emotion results. Each data item includes:
        - The input text passage to be classified.
        - The predicted emotion based on the text.
        - The probabilities of all possible emotions.
        - An emoji corresponding to the predicted emotion.

    features:
      - list_display:
          description: Show a list of input data and their prediction results.
          fields:
            - input_text: The input text passage.
            - predicted_emotion: The predicted emotion.
            - emotion_probabilities: Probabilities of all possible emotions.
            - emotion_emoji: Emoji corresponding to the predicted emotion.
      - input_function:
          description: Allow users to enter new text for emotion prediction.
          steps:
            - Enter a text passage.
            - Display the prediction result (emotion, emotion probabilities, emoji).

model_information:
  api_url: "http://34.142.220.207:8000/api/text-classification"
  name: j-hartmann/emotion-english-distilroberta-base
  description: The model was trained on 6 diverse datasets and predicts Ekman's 6 basic emotions, plus a neutral class.
  input_format: 
    type: json
    structure:
      texts:
        type: string
        description: A text passage written by the author.
  output_format: 
    description: A list of dict contains emotions (labels) and their corresponding scores (probabilities).
    type: List[dict]
    structure:
      label: 
        type: string
      score: 
        type: float
  parameters:
    config:
      id2label:
        "0": anger
        "1": disgust
        "2": fear
        "3": joy
        "4": neutral
        "5": sadness
        "6": surprise
      label2id:
        anger: 0
        disgust: 1
        fear: 2
        joy: 3
        neutral: 4
        sadness: 5
        surprise: 6

dataset_description:
  description: GoEmotions is a corpus of 58k carefully curated comments extracted from Reddit, with human annotations to 6 emotion categories or Neutral.
  data_source: ./data/goemotions.csv file
  data_format: 
    text: The text of the comment (with masked tokens, as described in the paper).
    id: The unique id of the comment.
    author: The Reddit username of the comment's author.
    subreddit: The subreddit that the comment belongs to.
    link_id: The link id of the comment.
    parent_id: The parent id of the comment.
    created_utc: The timestamp of the comment.
    rater_id: The unique id of the annotator.
    example_very_unclear: Whether the annotator marked the example as being very unclear or difficult to label (in this case they did not choose any emotion labels).
    emotions:
      anger: Binary label (0 or 1)
      disgusts: Binary label (0 or 1)
      fear: Binary label (0 or 1)
      joy: Binary label (0 or 1)
      neutral: Binary label (0 or 1)
      sadness: Binary label (0 or 1)
      surprise: Binary label (0 or 1)
"""

def test_generate_html_from_yaml() -> None:
    user_message = f"Generate the HTML UI for the following task:\n\n```yaml\n{task_yaml}\n```"

    res = graph.invoke(
        {"messages": [("system", system_prompt), ("user", user_message)]},
        {"configurable": {"system_prompt": system_prompt}},
    )

    html_content = str(res["messages"][-1].content).strip()

    if html_content.startswith("```html"):
        html_content = html_content.strip("```html").strip("```").strip()

    with open("generated_ui.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ HTML interface has been written to generated_ui.html.")
test_generate_html_from_yaml()