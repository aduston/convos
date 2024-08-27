from dataclasses import dataclass
from google.cloud.speech_v2.types import cloud_speech


@dataclass
class SpeakingTurn:
    """
    Represents a speaking turn in a conversation
    """
    speaker: str
    text: str
    end_time: float
    confidence: float
    is_echo: bool = False


def remove_echo(turns: list[SpeakingTurn]) -> list[SpeakingTurn]:
    """
    With a sample size of N=1, we've seen that speaker 2 sometimes has an echo
    that is reflected as speaker 1. The echo can be identified,
    I think, by a few factors:

    1. The echo end time stamp is very close to a speaker 2 time stamp.
    2. There are words in the echo repeated from the echoed text.
    3. The echoed confidence is low -- less than 0.7.

    Criterion 2 seems unreliable, so let's try eliminating just using
    criteria 1 and 3.
    """
    pass


def turn_multichannel_into_conversation(
    rec_results: cloud_speech.BatchRecognizeResults
) -> list[SpeakingTurn]:
    turns = [
        SpeakingTurn(
            result.channel_tag, 
            result.alternatives[0].transcript, 
            result.result_end_offset,
            result.alternatives[0].confidence,
        )
        for result in rec_results.results
        if len(result.alternatives) > 0
    ]
    turns = sorted(turns, key=lambda x: x.end_time)
    turns = remove_echo(turns)
