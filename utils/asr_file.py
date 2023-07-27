#!/usr/bin/env python3
#
# Copyright (c)  2023 by manyeyes

"""
This file demonstrates how to use sherpa-onnx Python API to transcribe
file(s) with a non-streaming model.


Please refer to
https://k2-fsa.github.io/sherpa/onnx/index.html
to install sherpa-onnx and to download the pre-trained models
used in this file.
"""
import argparse
import time
import wave
from pathlib import Path
from typing import Tuple

import numpy as np


def assert_file_exists(filename: str):
    assert Path(filename).is_file(), (
        f"{filename} does not exist!\n"
        "Please refer to "
        "https://k2-fsa.github.io/sherpa/onnx/pretrained_models/index.html to download it"
    )


def read_wave(wave_filename: str) -> Tuple[np.ndarray, int]:
    """
    Args:
      wave_filename:
        Path to a wave file. It should be single channel and each sample should
        be 16-bit. Its sample rate does not need to be 16kHz.
    Returns:
      Return a tuple containing:
       - A 1-D array of dtype np.float32 containing the samples, which are
       normalized to the range [-1, 1].
       - sample rate of the wave file
    """

    with wave.open(wave_filename) as f:
        assert f.getnchannels() == 1, f.getnchannels()
        assert f.getsampwidth() == 2, f.getsampwidth()  # it is in bytes
        num_samples = f.getnframes()
        samples = f.readframes(num_samples)
        samples_int16 = np.frombuffer(samples, dtype=np.int16)
        samples_float32 = samples_int16.astype(np.float32)

        samples_float32 = samples_float32 / 32768
        return samples_float32, f.getframerate()


def rec_file(sound_files, recognizer):
    print("Started!")
    start_time = time.time()

    streams = []
    total_duration = 0
    for wave_filename in sound_files:
        assert_file_exists(wave_filename)
        samples, sample_rate = read_wave(wave_filename)
        duration = len(samples) / sample_rate
        total_duration += duration

        s = recognizer.create_stream()
        s.accept_waveform(sample_rate, samples)

        tail_paddings = np.zeros(int(0.2 * sample_rate), dtype=np.float32)
        s.accept_waveform(sample_rate, tail_paddings)

        s.input_finished()

        streams.append(s)

    while True:
        ready_list = []
        for s in streams:
            if recognizer.is_ready(s):
                ready_list.append(s)
        if len(ready_list) == 0:
            break
        recognizer.decode_streams(ready_list)
    results = [recognizer.get_result(s) for s in streams]
    end_time = time.time()
    print("Done!")

    for wave_filename, result in zip(sound_files, results):
        print(f"{wave_filename}\n{result}")
        print("-" * 10)

    elapsed_seconds = end_time - start_time
    rtf = elapsed_seconds / total_duration
    print(f"Wave duration: {total_duration:.3f} s")
    print(f"Elapsed time: {elapsed_seconds:.3f} s")
    print(
        f"Real time factor (RTF): {elapsed_seconds:.3f}/{total_duration:.3f} = {rtf:.3f}"
    )

    return total_duration, results[0]


if __name__ == "__main__":
    rec_file(["audio_ac1_ar16k_s16le.wav"])
