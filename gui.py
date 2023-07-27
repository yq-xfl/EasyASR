import _thread
import argparse
import functools
import os
import time
import tkinter.messagebox
import wave
from tkinter import *
from tkinter.filedialog import *

import pyaudio
import sounddevice as sd
from utils.asr_file import rec_file
from utils.ini_recognizer import create_online_recognizer

# from data_utils.audio_process import AudioInferProcess
# from utils.audio_vad import crop_audio_vad
# from utils.predict import Predictor
# from utils.utility import add_arguments, print_arguments


class SpeechRecognitionApp:
    def __init__(self, window: Tk, args):
        self.window = window
        self.wav_path = None
        self.predicting = False
        self.playing = False
        self.recording = False
        self.stream = None
        self.to_an = True
        # 指定窗口标题
        self.window.title("kaldi语音识别")
        # 固定窗口大小
        self.window.geometry('870x500')
        self.window.resizable(False, False)
        # 识别短语音按钮
        self.short_button = Button(self.window, text="选择短语音识别", width=20, command=self.predict_audio_thread)
        self.short_button.place(x=10, y=10)
        # 识别长语音按钮
        # self.long_button = Button(self.window, text="选择长语音识别", width=20, command=self.predict_long_audio_thread)
        # self.long_button.place(x=170, y=10)
        # 录音按钮
        self.record_button = Button(self.window, text="录音识别", width=20, command=self.record_audio_thread)
        self.record_button.place(x=330, y=10)
        # 播放音频按钮
        # self.play_button = Button(self.window, text="播放音频", width=20, command=self.play_audio_thread)
        # self.play_button.place(x=490, y=10)
        # 输出结果文本框
        self.result_label = Label(self.window, text="输出日志：")
        self.result_label.place(x=10, y=70)
        self.result_text = Text(self.window, width=120, height=30)
        self.result_text.place(x=10, y=100)
        # 转阿拉伯数字控件
        self.an_frame = Frame(self.window)
        self.check_var = BooleanVar()
        self.to_an_check = Checkbutton(self.an_frame, text='中文数字转阿拉伯数字', variable=self.check_var, command=self.to_an_state)
        self.to_an_check.grid(row=0)
        self.to_an_check.select()
        self.an_frame.grid(row=1)
        self.an_frame.place(x=700, y=10)
        self.recognizer = create_online_recognizer()

    # 是否中文数字转阿拉伯数字
    def to_an_state(self):
        self.to_an = self.check_var.get()

    # 预测短语音线程
    def predict_audio_thread(self):
        if not self.predicting:
            self.wav_path = askopenfilename(filetypes=[("音频文件", "*.wav"), ("音频文件", "*.mp3")], initialdir='./dataset')
            if self.wav_path == '': return
            self.result_text.delete('1.0', 'end')
            self.result_text.insert(END, "已选择音频文件：%s\n" % self.wav_path)
            self.result_text.insert(END, "正在识别中...\n")
            _thread.start_new_thread(self.predict_audio, (self.wav_path, ))
        else:
            tkinter.messagebox.showwarning('警告', '正在预测，请等待上一轮预测结束！')

    # 预测短语音
    def predict_audio(self, wav_path):
        self.predicting = True
        try:
            start = time.time()
            duration, text = rec_file([wav_path], self.recognizer)
            self.result_text.insert(END, "消耗时间：%dms, 录音长度: %s\n" % (round((time.time() - start) * 1000), duration))
            self.result_text.insert(END, "识别结果：\n\n")
            self.result_text.insert(END, text)

        except Exception as e:
            print(e)
        self.predicting = False

    # 录音识别线程
    def record_audio_thread(self):
        if not self.recording:
            self.result_text.delete('1.0', 'end')
            _thread.start_new_thread(self.record_audio, ())
        else:
            # 停止播放
            self.recording = False
            self.record_button.configure(text='录音识别')

    def record_audio(self):
        self.record_button.configure(text='停止录音')
        self.recording = True

        self.result_text.insert(END, "开始实时语言识别...\n")
        # 录音参数
        sample_rate = 48000
        samples_per_read = int(0.1 * sample_rate)  # 0.1 second = 100 ms
        stream = self.recognizer.create_stream()
        last_result = ""
        with sd.InputStream(channels=1, dtype="float32", samplerate=sample_rate) as s:
            while True:
                samples, _ = s.read(samples_per_read)  # a blocking read
                samples = samples.reshape(-1)
                stream.accept_waveform(sample_rate, samples)
                while self.recognizer.is_ready(stream):
                    self.recognizer.decode_stream(stream)
                result = self.recognizer.get_result(stream)
                if last_result != result:
                    last_result = result
                    # self.result_text.insert(2.0, result)
                    self.result_text.replace(2.0, INSERT, result)

                if not self.recording:
                    self.result_text.insert(END, "\n结束录音")
                    break


tk = Tk()
args = {}
myapp = SpeechRecognitionApp(tk, args)

if __name__ == '__main__':
    tk.mainloop()

