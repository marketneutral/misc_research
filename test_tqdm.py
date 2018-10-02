import pandas as pd
import numpy as np
from tqdm import tqdm

df = pd.DataFrame(np.random.randint(0, 100, (1000000, 6)))
tqdm.pandas(desc="my bar!")
my_df = df.progress_apply(lambda x: x**2)
