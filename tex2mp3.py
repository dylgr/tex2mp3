import argparse
import os
import re
import time
import logging

import boto3
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EQUATION_PATTERN = re.compile(r"(\$\$[^\$]*\$\$|\$[^\$]*\$)")

PROMPT = """Convert the following LaTeX expression to plain text for TTS.
INPUT: $$\\mathrm{FFN}(x)=\\max(0, xW_1 + b_1) W_2 + b_2$$
OUTPUT: F F N of x is equal to the maximum of 0 and the product of x and W sub 1 added to b sub 1, all multiplied by W sub 2 and added to b sub 2
INPUT: %s
OUTPUT:"""

def read_file(filename):
    """Read the content of a file and return it."""
    with open(filename, 'r') as file:
        content = file.read()
    return content


def transcribe_equation(text, model):
    """Transcribe an equation to plain text."""
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT % text}]
    )
    return completion.choices[0].message.content


def replace_equations(text, model):
    """Replace equations in the text with their transcriptions."""
    matches = EQUATION_PATTERN.findall(text)
    matches = list(set(matches))
    num_equations = len(matches)
    for i, match in enumerate(matches):
        new_equation_text = transcribe_equation(match, model).rstrip('.')
        text = text.replace(match, new_equation_text)
        logger.info('(%s/%s) from: %s\n', i, num_equations, match)
        logger.info('(%s/%s) to: %s\n', i, num_equations, new_equation_text)
    return text


def synthesize_speech(text, s3_bucket, voice_id, audio_format):
    """Synthesize speech using Amazon Polly and return the task ID."""
    polly_client = boto3.client('polly')
    response = polly_client.start_speech_synthesis_task(
        Text=text,
        OutputS3BucketName=s3_bucket,
        VoiceId=voice_id,
        OutputFormat=audio_format
    )
    return response['SynthesisTask']['TaskId']


def download_audio(task_id, s3_bucket, output, max_tries=20, sleep_time=5):
    """Download the synthesized audio from the given S3 bucket."""
    polly_client = boto3.client('polly')
    s3 = boto3.client('s3')

    for _ in range(max_tries):
        response = polly_client.get_speech_synthesis_task(TaskId=task_id)
        if response['SynthesisTask']['TaskStatus'] == 'completed':
            s3.download_file(s3_bucket, f"{task_id}.mp3", output)
            break
        if response['SynthesisTask']['TaskStatus'] == 'failed':
            raise Exception("Polly TTS Task Failed")
        time.sleep(sleep_time)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Name of input markdown file.", required=True)
    parser.add_argument("-o", "--output", type=str, help="Name of output audio file.", required=True)
    parser.add_argument("-s", "--s3-bucket", type=str, help="s3 bucket to write the audio file to.", required=True)
    parser.add_argument("-m", "--model", type=str, help="OpenAI model name.", required=False, default='gpt-3.5-turbo')
#    parser.add_argument("-p", "--prompt", type=str, help="Prompt used to convert equations to text.", required=False, default=PROMPT)
    parser.add_argument("-v", "--voice-id", type=str, help="AWS Polly voice ID.", required=False, default="Joanna")
    parser.add_argument("-f", "--audio-format", type=str, help="Audio output format.", required=False, default='mp3')
    args = parser.parse_args()

    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(PROMPT)
    raw_text = read_file(args.input)
    processed_text = replace_equations(raw_text, args.model)
    task_id = synthesize_speech(processed_text, args.s3_bucket, args.voice_id, args.audio_format)
    download_audio(task_id, args.s3_bucket, args.output)

if __name__ == "__main__":
    main()
