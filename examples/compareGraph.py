from GraphMaker import GraphMaker
from StatsScraper import StatsScraper

ss = StatsScraper("skyprompdvorak")
gm = GraphMaker(ss.getData())

ss2 = StatsScraper("typeracer")
gm2 = GraphMaker(ss2.getData())

gm.overlapWPM(gm2, cutoff=True, self_name="skyprompdvorak", other_name="typeracer")