#!/usr/bin/env python

import json
import sys

def create_readable_transcript(left_response, right_response, pretty_output_file):
    _write_pretty(create_json_transcript(left_response, right_response), pretty_output_file)

def create_json_transcript(left_response, right_response):
    left_extract = _create_extract(left_response, "left")
    right_extract = _create_extract(right_response, "right")
    return _create_combined_extract(left_extract, right_extract)

def _create_extract(watson_response, speaker):
    watson_results = watson_response["results"][0]["results"]
    results = []
    for watson_result in watson_results:
        alt = watson_result["alternatives"][0]
        transcript = alt["transcript"]
        timestamp = alt["timestamps"][0][1]
        results.append(
            dict(timestamp=timestamp, transcript=transcript, speaker=speaker))
    return results

def _create_combined_extract(left, right):
    return sorted(left + right, key=lambda x: x['timestamp'])

def _write_pretty(combined, output_file):
    speaker = None
    for utterance in combined:
        if utterance["speaker"] != speaker:
            speaker = utterance["speaker"]
            if speaker is not None:
                output_file.write("\n")
            output_file.write(speaker)
            output_file.write(" (")
            output_file.write(_format_timestamp(utterance["timestamp"]))
            output_file.write(")\n\n")
        transcript = utterance['transcript'].replace(
            "%HESITATION", "").strip()
        if transcript != "":
            output_file.write(transcript)
            output_file.write("\n")

def _format_timestamp(ts):
    ts = int(ts)
    minutes = ts / 60
    seconds = ts % 60
    return "{0}:{1:02d}".format(minutes, seconds)

if __name__ == '__main__':
    create_readable_transcript(sys.argv[1], sys.argv[2], sys.argv[3])
