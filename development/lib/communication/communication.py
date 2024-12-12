import struct

class Communication:
    class Command(int):
      INIT = 0
      OK = 1

      START_SAMPLING=100
      STOP_SAMPLING=101
      SET_FLUSH=102
      SET_INHALE=103

      ERR_INIT = 200
      ERR_SAMPLING = 201

    @staticmethod
    def toByte(cmd : Command, val : int):
      return struct.pack("ii", cmd, val)

    @staticmethod
    def toNumber(msg) -> tuple[Command, int]:
      return struct.unpack("ii", msg)