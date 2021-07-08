from contextlib import contextmanager

import yaml

from blinker import Namespace
from cornell.cornell_helpers import saved_data_to_yaml


cornell_signals = Namespace()

# Supported Signals:
logging_setup = cornell_signals.signal("logging_setup")
process_cassette_file = cornell_signals.signal("process_cassette_file")


class MultipleSignalSubscribers(Exception):
    pass


class SignalNotRegistered(Exception):
    pass


def on_cornell_exit(app):
    if app.config.record:
        index_dict = yaml.safe_load(app.config.index_file.read_text())
        index_dict.update(dict(app.config.cassette_paths))
        saved_data_to_yaml(index_dict, app.config.index_file)
        app.logger.info("Index file was updated", index_file_path=app.config.index_file)


@contextmanager
def signal_context(signal_name, *args, **kwargs):
    pending_signal = cornell_signals.get(signal_name)
    if not pending_signal:
        raise SignalNotRegistered(f"Signal {signal_name} not registered")

    if len(pending_signal.receivers) > 1:
        raise MultipleSignalSubscribers(f"Only one subscriber allowed for {signal_name}. Found: {pending_signal.receivers}")

    results = pending_signal.send(*args, **kwargs)
    yield results[0][1] if results else None
