import sherpa_onnx
from .tools import assert_file_exists

encoder = "models/encoder-epoch-99-avg-1.onnx"
decoder = "models/decoder-epoch-99-avg-1.onnx"
joiner = "models/joiner-epoch-99-avg-1.onnx"
tokens = "models/tokens.txt"
decoding_method = "greedy_search"
num_threads = 1

assert_file_exists(encoder)
assert_file_exists(decoder)
assert_file_exists(joiner)
assert_file_exists(tokens)


def create_online_recognizer():
    recognizer = sherpa_onnx.OnlineRecognizer(
        tokens=tokens,
        encoder=encoder,
        decoder=decoder,
        joiner=joiner,
        num_threads=num_threads,
        sample_rate=16000,
        feature_dim=80,
        decoding_method=decoding_method,
    )
    return recognizer

