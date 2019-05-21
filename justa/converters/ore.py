from base import FileExtractor
from ore_ce import MPECEFileExtractor, TJECEFileExtractor
from ore_pr import DPEPRFileExtractor, MPEPRFileExtractor, TJEPRFileExtractor
from ore_sp import DPESPFileExtractor, MPESPFileExtractor, TJESPFileExtractor


FileExtractor.register(DPEPRFileExtractor)
FileExtractor.register(DPESPFileExtractor)
FileExtractor.register(MPECEFileExtractor)
FileExtractor.register(MPEPRFileExtractor)
FileExtractor.register(MPESPFileExtractor)
FileExtractor.register(TJECEFileExtractor)
FileExtractor.register(TJEPRFileExtractor)
FileExtractor.register(TJESPFileExtractor)
