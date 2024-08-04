from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")

    args = parser.parse_args()
    SAMPLE_TOPIC = args.topic
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    try:
        response = generate_script(SAMPLE_TOPIC)
        logging.info("Script generated: %s", response)

        asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))
        logging.info("Audio generated: %s", SAMPLE_FILE_NAME)

        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        logging.info("Timed captions generated: %s", timed_captions)

        search_terms = getVideoSearchQueriesTimed(response, timed_captions)
        logging.info("Search terms generated: %s", search_terms)

        if search_terms:
            background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
            logging.info("Background video URLs: %s", background_video_urls)
        else:
            background_video_urls = []
            logging.warning("No background video search terms found")

        background_video_urls = merge_empty_intervals(background_video_urls)
        logging.info("Processed background video URLs: %s", background_video_urls)

        if background_video_urls:
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
            logging.info("Video generated: %s", video)
        else:
            logging.warning("No video generated")

    except Exception as e:
        logging.error("An error occurred: %s", e)
