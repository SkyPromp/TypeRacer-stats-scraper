from GraphMaker import GraphMaker
from StatsScraper import StatsScraper

ss = StatsScraper("skyprompdvorak")
gm = GraphMaker(ss.getData())

smoothing = 50

gm.plotWPM(average_grouping=50)
gm.plotAccuracy(average_grouping=50)
gm.plotWPMAccCorrelation()
gm.plotAccWPMCorrelation()
gm.histDailyRaceAmounts()
gm.histWPM()
gm.histAccuracy()
gm.dailyProgress()
