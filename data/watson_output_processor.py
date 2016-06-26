#!/usr/bin/env python

import json
import sys

def create_readable_transcript(left_file, right_file, pretty_output_file):
    _write_pretty(create_combined(left_file, right_file), pretty_output_file)

def create_json_transcript(left_file, right_file):
    left_extract = _create_extract(left_file, "left")
    right_extract = _create_extract(right_file, "right")
    return _create_combined_extract(left_extract, right_extract)

def _create_extract(watson_file, speaker):
    with open(watson_file, "r") as f:
        watson_obj = json.loads(f.read())
    watson_results = watson_obj["results"][0]["results"]
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
    with open(output_file, "w") as f:
        for utterance in combined:
            if utterance["speaker"] != speaker:
                speaker = utterance["speaker"]
                if speaker is not None:
                    f.write("\n")
                f.write(speaker)
                f.write(" (")
                f.write(_format_timestamp(utterance["timestamp"]))
                f.write(")\n\n")
            transcript = utterance['transcript'].replace(
                "%HESITATION", "").strip()
            if transcript != "":
                f.write(transcript)
                f.write("\n")

def _format_timestamp(ts):
    ts = int(ts)
    minutes = ts / 60
    seconds = ts % 60
    return "{0}:{1:02d}".format(minutes, seconds)

if __name__ == '__main__':
    create_readable_transcript(sys.argv[1], sys.argv[2], sys.argv[3])
