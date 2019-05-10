import os
from pathlib import Path


PROJECT_DATA_PATH = Path(__file__).parent.parent.parent / "data"
DROPBOX_DATA_PATH = Path(os.path.expanduser("~")) / "Dropbox/Justa_dados/Dados/"
ORE_DATA_PATH = DROPBOX_DATA_PATH / "ETAPA_0/Eixo_ORE"
