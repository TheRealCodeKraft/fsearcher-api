# coding: utf8

import numpy as np

import pandas as pd

def read_prenom_file(src_path):
    df = pd.read_csv(src_path, sep='\t', encoding='UTF8',
                     dtype={'sexe': str})

    c = df['annais'].str.contains('X')
    c |= df['dpt'].str.contains('X')
    c |= (df['preusuel'] == '_PRENOMS_RARES')
    df = df.loc[~c]
    df['annais'] = df['annais'].astype(int)

    return df

def score_temporel(df, prenom, sexe=None, depuis=None):
    """Distance entre les profils temporels des prénoms"""
    
    dft = df.drop(['sexe', 'dpt'], axis='columns') \
            .pivot_table(values='nombre', aggfunc='sum', columns='preusuel',
                         index='annais') \
            .fillna(0.)
    
    dft = dft.divide(dft.max(axis='rows'), axis='columns')
    
    dft = dft.subtract(dft[prenom.upper()], axis='rows')
    
    return (1 - np.sqrt(np.square(dft).sum(axis='rows') / dft.shape[0])).sort_values()

def score_geo(df, prenom, sexe=None, depuis=None):
    """Distance entre les profils géographiques des prénoms"""
    
    dft = df.drop(['sexe', 'annais'], axis='columns') \
            .pivot_table(values='nombre', aggfunc='sum', columns='preusuel',
                         index='dpt') \
            .fillna(0.)
    
    # Normer par le nombre total de naissances dans chaque département
    dft = dft.divide(dft.sum(axis='columns'), axis='rows')
    
    # Ramener chaque profil géographique entre 0 et 1
    dft = dft.divide(dft.max(axis='rows'), axis='columns')

    # Calculer la distance algébrique au prénom recherché
    dft = dft.subtract(dft[prenom.upper()], axis='rows')
    
    # Prendre la norme
    return (1 - np.sqrt(np.square(dft).sum(axis='rows') / dft.shape[0])).sort_values()

def score_popularite(df, prenom, sexe=None, depuis=None):
    """Distance entre les nombres de prénoms donnés"""
    
    dft = df.groupby('preusuel')['nombre'].sum()
    
    dft = dft / dft[prenom.upper()]
    
    return np.exp2(-np.abs(np.log2(dft))).sort_values()

def score(df, prenom, sexe=None, depuis=None):

    dft = df

    if sexe is not None:
        if sexe == 'M':
            c = (dft['sexe'] == '1')
            c |= (dft['preusuel'] == prenom.upper())

        elif sexe == 'F':
            c = (dft['sexe'] == '1')
            c |= (dft['preusuel'] == prenom.upper())
        else:
            msg = ("Sex parameter should be 1, 2 or None.")
            raise ValueError(msg)
        
        dft = dft.loc[c]

    if depuis is not None:
        c = (dft['annais'] >= depuis)
        dft = dft.loc[c]

    sc = score_geo(dft, prenom, sexe, depuis)
    sc *= score_temporel(dft, prenom, sexe, depuis)
    sc *= score_popularite(dft, prenom, sexe, depuis)

    return sc.sort_values(ascending=False).head(20)

def nombre_par_an(df, prenom):
    """Nombre de naissances ayant ce prénom chaque année."""
    c = (df['preusuel'] == prenom.upper())
    
    if c.sum() == 0:
        msg = ("Prénom inconnu : {}".format(prenom.capitalize()))
        raise ValueError(msg)

    dft = df.sum()

    return dft.pivot_table(values='nombre', aggfunc='sum', index='annais',
                           columns='sexe')
