from dataclasses import dataclass
from google.cloud.speech_v2.types import cloud_speech


@dataclass
class SpeakingTurn:
    """
    Represents a speaking turn in a conversation
    """
    speaker: int
    text: str
    end_time: float
    confidence: float
    is_echo: bool = False


def is_echo(potential_echo: SpeakingTurn, echoeds: list[SpeakingTurn]) -> bool:
    """
    Returns True if the potential echo is an echo of the echoed turns
    """
    if len(echoeds) == 0:
        return False
    return any(abs(echoed.end_time - potential_echo.end_time) < 2.0
               for echoed in echoeds)


def mark_echoes(turns: list[SpeakingTurn]) -> None:
    """
    With a sample size of N=1 convo, we've seen that speaker 2 sometimes has
    an echo that is reflected as speaker 1. The echo can be identified,
    I think, by a few factors:

    1. The echo end time stamp is very close to a speaker 2 time stamp.
    2. There are words in the echo repeated from the echoed text.
    3. The echoed confidence is low -- less than 0.8.

    Criterion 2 seems unreliable, so let's try eliminating just using
    criteria 1 and 3.
    """
    echo_candidate_indices = [
        i
        for i, turn in enumerate(turns)
        if turn.speaker == 1 and turn.confidence < 0.8
    ]
    for index in echo_candidate_indices:
        potentially_echoed_indices = []
        if index > 0 and turns[index - 1].speaker == 2:
            potentially_echoed_indices.append(index - 1)
        if index < len(turns) - 1 and turns[index + 1].speaker == 2:
            potentially_echoed_indices.append(index + 1)
        if is_echo(
                turns[index],
                [turns[i] for i in potentially_echoed_indices]):
            turns[index].is_echo = True


def turn_multichannel_into_conversation(
    rec_results: cloud_speech.BatchRecognizeResults
) -> list[SpeakingTurn]:
    turns = [
        SpeakingTurn(
            result.channel_tag,
            result.alternatives[0].transcript,
            result.result_end_offset.ToMilliseconds() / 1000.0,
            result.alternatives[0].confidence,
        )
        for result in rec_results.results
        if len(result.alternatives) > 0
    ]
    turns = sorted(turns, key=lambda x: x.end_time)
    mark_echoes(turns)
    return turns
