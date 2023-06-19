import pandas as pd

df = pd.DataFrame({'col1': ['abc', 'def', 'tre'],
                   'col2': ['foo', 'bar', 'stuff']})

print(df.values.tolist())