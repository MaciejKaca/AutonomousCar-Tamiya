class Converter:
    __SOURCE_MAX = int()
    __SOURCE_MIN = int()
    __TARGET_MIN = int()
    __TARGET_MAX = int()
    __SCALE = float()

    # def __init__(self, source_min : int, source_max : int, target_min : int, target_max : int):
    #     self.__SOURCE_MIN = source_min
    #     self.__SOURCE_MAX = source_max

    #     self.__TARGET_MIN = target_min
    #     self.__TARGET_MAX = target_max

    #     self.__SCALE = (self.__TARGET_MAX - self.__TARGET_MIN) / (self.__SOURCE_MAX - self.__SOURCE_MIN)

    # def getTargetValue(self, number) -> int:
    #     if number > self.__SOURCE_MAX:
    #         return self.__TARGET_MAX

    #     if number < self.__SOURCE_MIN:
    #         return self.__TARGET_MIN 

    #     return int((self.__TARGET_MAX - ((self.__SOURCE_MAX - number) * self.__SCALE)))

    def __init__(self, source_min : int, source_max : int, target_min : int, target_max : int):
        self.__SOURCE_MIN = source_min
        self.__SOURCE_MAX = source_max

        self.__TARGET_MIN = target_min
        self.__TARGET_MAX = target_max

        self.__SCALE = (self.__TARGET_MAX - self.__TARGET_MIN) / (self.__SOURCE_MAX - self.__SOURCE_MIN)

    def getTargetValue(self, number) -> int:
        if number > self.__SOURCE_MAX:
            return self.__TARGET_MAX

        if number < self.__SOURCE_MIN:
            return self.__TARGET_MIN 

        return int((self.__TARGET_MAX - ((self.__SOURCE_MAX - number) * self.__SCALE)))