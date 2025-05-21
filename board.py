import time
import pyfirmata2

class ArduinoController:
    def __init__(self, port=None):
        """
        Initializes the connection with Arduino.
        If no port is specified, it attempts to autodetect.
        """
        self.board = pyfirmata2.Arduino(port or pyfirmata2.auto_setup())
        self.iterator = pyfirmata2.util.Iterator(self.board)
        self.iterator.start()

        # Dictionaries to store components
        self.servos = {}
        self.motors = {}
        self.leds = {}
        self.buzzers = {}
        self.gas_sensors = {}  # Nuevo diccionario para sensores de gas

    def setup_led(self, pin: int):
        """Configures an LED on the specified pin."""
        self.leds[pin] = self.board.get_pin(f'd:{pin}:o')

    def led_on(self, pin: int):
        """Turns on the LED."""
        self.leds[pin].write(1)

    def led_off(self, pin: int):
        """Turns off the LED."""
        self.leds[pin].write(0)

    def setup_buzzer(self, pin: int):
        """Configures a buzzer on the specified pin."""
        self.buzzers[pin] = self.board.get_pin(f'd:{pin}:o')

    def buzzer_on(self, pin: int):
        """Activates the buzzer."""
        self.buzzers[pin].write(1)

    def buzzer_off(self, pin: int):
        """Deactivates the buzzer."""
        self.buzzers[pin].write(0)

    def setup_servo(self, pin: int):
        """Configures a servo on the specified pin."""
        self.servos[pin] = self.board.get_pin(f'd:{pin}:s')  # Servo mode
        time.sleep(0.1)  # Small pause for initialization

    def set_servo_angle(self, pin: int, angle: float):
        """Sets the servo angle (0-180 degrees)."""
        self.servos[pin].write(angle)

    def setup_motor(self, in1_pin: int, in2_pin: int, motor_id: str, enb_pin: int):
        """
        Configures a DC motor using the DRV8833 driver.
        For DRV8833, two control signals (in1 and in2) are used.
        The motor_id is an identifier for storing this motor's configuration.
        """
        self.motors[motor_id] = {
            'in1': self.board.get_pin(f'd:{in1_pin}:o'),  # PWM capable pin
            'in2': self.board.get_pin(f'd:{in2_pin}:o'),   # PWM capable pin
            'eb': self.board.get_pin(f'd:{enb_pin}:p')     # PWM capable pin
        }

    def set_motor_speed(self, motor_id: str, speed: int):
        """
        Controls the speed and direction of the motor (-255 to 255) using DRV8833.
        If speed > 0: forward, if speed < 0: reverse, and if speed == 0: stop.
        """
        speed = speed / 100
        normalized_speed = abs(speed) / 255.0  # Normalize to 0-1 for PWM

        motor = self.motors[motor_id]

        if speed > 0:
            motor['eb'].write(speed)
            motor['in1'].write(1)
            motor['in2'].write(0)
        elif speed < 0:
            motor['eb'].write(abs(speed))
            motor['in1'].write(0)
            motor['in2'].write(1)
        else:
            motor['eb'].write(0)
            motor['in1'].write(0)
            motor['in2'].write(0)

    ### NUEVO - Sensor de Gas (MQ2)
    def setup_gas_sensor(self, pin: int, sensor_id: str):
        """
        Configures an analog pin for reading from a gas sensor (e.g., MQ2).
        - pin: Analog pin number (A0, A1, etc.)
        - sensor_id: Identifier for this sensor (for multiple sensors)
        """
        self.gas_sensors[sensor_id] = self.board.get_pin(f'a:{pin}:i')  # 'i' = input

    def read_gas_sensor(self, sensor_id: str) -> int:
        """
        Reads and returns the raw analog value from the specified gas sensor.
        Returns an integer between 0 and 1023.
        """
        if sensor_id not in self.gas_sensors:
            raise ValueError(f"Sensor ID '{sensor_id}' no está configurado.")

        return self.gas_sensors[sensor_id].read() * 1023  # Devuelve valor entero entre 0 y 1023

    ### Fin de nuevo código

    def close(self):
        """Closes the connection with Arduino."""
        self.iterator.stop()
        self.board.exit()