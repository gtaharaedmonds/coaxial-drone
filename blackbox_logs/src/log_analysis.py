import scipy.io
import numpy as np
import matplotlib.pyplot as plt


TIME_LABEL_MSG_NAME = "BAT_label"
TIME_DATA_MSG_NAME = "BAT_0"
TIME_SIGNAL_NAME = "LineNo"


class Log:
    def __init__(self, file_path):
        self.log = scipy.io.loadmat(file_path)  # Load .mat file

    def _get_labels_from_msg(self, label_msg):
        """
        Given the name of the label message, return an np array of the labels.
        """
        return np.array([val[0][0] for val in self.log[label_msg]])

    def _get_signal_data(self, label_msg_name, data_msg_name, signal_name):
        """
        Get the data for a signal in a msg.
        """
        labels = self._get_labels_from_msg(label_msg_name)  # Get all labels
        signal_idx = np.where(labels == signal_name)[0][0]  # Get index of match
        return self.log[data_msg_name][:, signal_idx]

    def _get_raw_time(self):
        """
        Get the unscaled log time values, in seconds.
        """
        time_us = self._get_signal_data(
            TIME_LABEL_MSG_NAME, TIME_DATA_MSG_NAME, TIME_SIGNAL_NAME
        )
        print(time_us)
        return time_us / 1e3  # to s

    def print_msgs(self):
        """
        Print all msgs in a log.
        """
        print("\n".join(self.log.keys()))

    def print_labels(self, label_msg_name):
        """
        Print all labels for a msg type.
        """
        for i, signal in enumerate(self._get_labels_from_msg(label_msg_name)):
            print(f"{i}: {signal}")

    def get_data(self, label_msg_name, data_msg_name, signal_name, start=0, end=1e12):
        """
        Get the time-series data for a signal in a msg.
        Returns (time, signal)
        """
        time_data = self._get_raw_time()
        signal_data = self._get_signal_data(label_msg_name, data_msg_name, signal_name)

        # Find start index
        start_i = 0
        for i, time in enumerate(time_data):
            if time >= start:
                start_i = i
                break

        # Find end index
        end_i = len(time_data)
        for i, time in enumerate(time_data):
            if time >= end:
                end_i = i
                break

        return time_data[start_i:end_i], signal_data[start_i:end_i]
