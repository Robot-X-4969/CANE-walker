from src.newUltrasonic import *
from src.sound import *

sideOpt = DistanceOptions()
sideOpt.minDistance = 0.02
sideOpt.maxDistance = 1.0
sideOpt.inverseConstant = 0.3
frontOpt = DistanceOptions()
frontOpt.minDistance = 0.25
frontOpt.maxDistance = 3.5
frontOpt.inverseConstant = 1

leftSideSound = SoxSoundThread("sound/98left.wav")
leftFrontSound = SoxSoundThread("sound/884left.wav")
rightFrontSound = SoxSoundThread("sound/884right.wav")
rightSideSound = SoxSoundThread("sound/98right.wav")

thread = UltrasonicThread([23,            23,             18,              18],
                          [16,            21,             12,              24],
                          [sideOpt,       frontOpt,       frontOpt,        sideOpt],
                          [leftSideSound, leftFrontSound, rightFrontSound, rightSideSound])
#thread = UltrasonicThread([23], [16], [sideOpt], [leftSideSound])

thread.start()
thread.join()
