# making now ...
import threading
import os
import RPi.GPIO as GPIO
import pygame.mixer

class BoardInfo(object):
    STATE_LED = 1
    STATE_BLUE = 2
    STATE_FLASH = 3

    def __init__(self, sw_pin=18, led_LED_pin=21, blue_LED_pin=20):
        self.sw_pin = sw_pin
        self.led_LED_pin = led_LED_pin
        self.blue_LED_pin = blue_LED_pin
        self.init_rasp_board()
        self._sign_state = self.STATE_LED

    def __del__(self):
        self.output_led(0)
        self.output_blue(0)

    def init_rasp_board(self):
        try:
            #GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.sw_pin, GPIO.IN)
            GPIO.setup(self.led_LED_pin, GPIO.OUT)
            GPIO.setup(self.blue_LED_pin, GPIO.OUT)
        except:
            print('Error: ボードにPINが刺さっていないか、ボードが設置されていません')
            raise

    @property
    def sign_state(self):
        return self._sign_state

    @sign_state.setter
    def sign_state(self, sign_state):
        if sign_state not in range(1, 3):
            raise ValueError('boardに指定しようとしたステータス値が不正です')
        self._sign_state = sign_state

    def output_blue_flash(self, state):
        if not state:
            self.output_blue(0)
        self.output_blue(1)
        time.sleep(0.2)
        self.output_blue(0)

    def output_led(self, state)
        GPIO.output(self.led_LED_pin, state)

    def output_blue(self, state)
        GPIO.output(self.blue_LED_pin, state)

    def input_led(self):
        return GPIO.input(self.led_LED_pin)

    def input_blue(self):
        return GPIO.input(self.blue_LED_pin)

    def input_sw(self):
        return GPIO.input(self.sw_pin)


class PedestrianSigns(object):
    """
    This class is Singleton.
    But you can change the board information with DI.
    """
    _instance = None
    _lock = threading.Lock()

    GUIDE_VOICE = 'guide_voice.wav'
    GUIDE_VOICE_MESSAGE = 'まもなく信号が赤になります'
    GUIDE_ALERT = 'guide_alert.mp3'

    # Change board info with DI
    def __init__(self, board_info):
        self.board_info = board_info

    def __new__(cls):
        # Thread safe
        with cls._lock:
            if cls._instance is not None:
                return cls._instance

            cls._instance = super().__new__(cls)
            cls._instance.init_music()
        return cls._instance


    # Initialize pygame & music file
    def init_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("guide_alert.mp3")

        if not os.path.isfile(GUIDE_SOUND):
            make_voice_wav(GUIDE_VOICE, GUIDE_VOICE_MESSAGE)


    # Make guide voice from message
    def make_voice_wav(self, file_name, message):
        jtalk_option="\
            -m /usr/share/hts-voice/mei/mei_normal.htsvoice \
            -x /var/lib/mecab/dic/open-jtalk/naist-jdic \
            -ow {}".format(file_name)
        os.system("echo {} | open_jtalk {}".format(message, jtalk_option))

    def sign_led(self):
        self.board_info.output_blue(0)
        self.board_info.output_led(1)
        self.board_info.sign_state = self.board_info.STATE_LED
        self.func_timer = None

    def alert_led(self):
        print('warning red!')

    def sign_blue_flash(self):
        self.board_info.output_blue(1)
        time.sleep(0.2)
        self.board_info.output_blue(0)
        self.board_info.sign_state = self.board_info.STATE_FLASH

    def sign_blue(self):
        self.board_info.output_led(0)
        self.board_info.output_blue(1)
        self.board_info.sign_state = self.board_info.STATE_BLUE
        print('pappo-')

    def start():
        while True:
            # stateが赤で、赤のLEDが未点灯であれば
            if self.board_info.sign_state == self.board_info.STATE_LED and self.board_info.input_led() == 0:
                self.board_info.output_led(1)

            # 永続待機状態で、SWを押されたら信号が青
            if self.board_info.input_sw() == 1 and self.func_timer is None:
                self.func_timer = FuncExecTimer(2, sign_blue)
            # 青になるtimerが実行終了状態で、stateが青のとき
            if self.func_timer.executed and self.board_info.sign_state == self.board_info.STATE_BLUE:
                FuncExecTimer(2, alert_led)
                self.func_timer = FuncExecTimer(5, sign_blue_flash)
            # stateが点滅の時
            if self.board_info.sign_state == self.board_info.STATE_FLASH:
                # stateがflashに変更した瞬間のみ
                if self.func_timer.executed:
                    self.func_timer = FuncExecTimer(2, sign_led)
                sign_blue_flash()


class FuncExecTimer(object):
    def __init__(self, time_sec, func, *args):
        self.time_sec = time_sec
        self.func = func
        self.func_args = args
        self._executed = False
        self.start()

    @property
    def executed(self):
        return self._executed

    def start(self):
        signal.signal(signal.SIGALRM, signal_wrapper(self.func))
        signal.settimer(signal.ITIMER_REAL, self.time_sec)

    def signal_wrapper(self, func):
        def wrapper():
            self._executed = True
            func(self.func_args)
        return wrapper

if __name__ = '__main__':
    try:
        board_info = BoardInfo()
        pedestrian_signs = PedestrianSigns(board_info)
        pedestrian_signs.start()
    except KeyboardInterrupt:
        print('終了します')


