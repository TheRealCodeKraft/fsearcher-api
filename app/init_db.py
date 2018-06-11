import pandas as pd

import progressbar

from prenoms import read_prenom_file, score

from sqlalchemy import create_engine

def main():
    print("--> Reading first names file from 1900 to 2015 (takes time).")
    df = read_prenom_file('assets/dpt2016.txt')
    print("--> {n} first names loaded!".format(n=df['preusuel'].nunique()))

    engine = create_engine('sqlite:///assets/data.sqlite')
    connection = engine.connect()

    bar = progressbar.ProgressBar(max_value=df['preusuel'].nunique())
    for idx, prenom in enumerate(df['preusuel'].unique()):
        for sex in ['M', 'F']:
            stmp = score(df, prenom, sex).head(50)
            
            res = pd.DataFrame({
                'preusuel': prenom,
                'sex': sex,
                'preusuel2': stmp.index,
                'score': stmp.values
            })

            res.to_sql("scores", connection,
                       if_exists='replace' if idx == 0 else 'append',
                       index=False)

        bar.update(idx)

    connection.close()

    bar.finish()

if __name__ == '__main__':
    main()
