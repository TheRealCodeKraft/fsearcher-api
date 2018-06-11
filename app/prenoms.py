# coding: utf8
from functools import lru_cache

import numpy as np

import pandas as pd

def read_prenom_file(src_path):
    '''
    Reading file
    '''
    df = pd.read_csv(src_path, sep='\t', encoding='UTF8',
                     dtype={'sexe': str})

    '''
    Movling particular lines out
    '''
    c = df['annais'].str.contains('X')
    c |= df['dpt'].str.contains('X')
    c |= (df['preusuel'] == '_PRENOMS_RARES')
    df = df.loc[~c]
    df['annais'] = df['annais'].astype(int)

    '''
    Removing rare names
    '''
    dft = df.groupby(['preusuel', 'sexe'])['nombre'].sum().reset_index()

    dft.loc[:, 'idx'] = dft['preusuel'] + dft['sexe']
    rares = dft.loc[dft['nombre'] < 20]['idx']

    df.loc[:, 'idx'] = df['preusuel'] + df['sexe']
    df = df.loc[~df['idx'].isin(rares)]
    del df['idx']

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
            c = (dft['sexe'] == '2')
            c |= (dft['preusuel'] == prenom.upper())
        else:
            msg = ("Sex parameter should be 'M', 'F' or None.")
            raise ValueError(msg)
        
        dft = dft.loc[c]

    if depuis is not None:
        c = (dft['annais'] >= depuis)
        dft = dft.loc[c]

    sc = score_geo(dft, prenom, sexe, depuis)
    sc *= score_temporel(dft, prenom, sexe, depuis)
    sc *= score_popularite(dft, prenom, sexe, depuis)

    return sc.sort_values(ascending=False)

# @lru_cache(maxsize=128)
def score_filter(df, prenom, sexe=None, depuis=None, exclude=None,
                 startswith=None, endswith=None, not_startswith=None,
                 not_endswith=None, contains=None, not_contains=None,
                 min_length=None, max_length=None, composed=None):
    """Finds and sorts closest matching names, possibly filtering some.

    Arguments:
    df -- the pandas DataFrame containing raw names statistical data
    prenom -- the name to match
    sexe -- the gender of the names to look for
    depuis -- the start year for stats to use
    exclude -- a list of names to exclude from search (AND)
    startswith -- a list of strings the names should start with (OR)
    endswith -- a list of strings the names should end with (OR)
    not_startswith -- a list of strings the names should not start with (AND)
    not_endswith -- a list of strings the names should not end with (AND)
    contains -- a list of strings the name should contain (OR)
    not_contains -- a list of strings the name should not contain (AND)
    min_length -- Minimum number of characters in the name (including hyphens)
    max_length -- Maximum number of characters in the name (including hyphens)
    composed -- Names that are composed (should be True, False or None)

    Returns:
    A pandas Series of names and scores.
    """
    # Apply score function
    sc = score(df, prenom, sexe, depuis)

    def check_is_list(ll):
        if not isinstance(ll, list):
            msg = "This should be a list of strings."
            raise TypeError(msg)

    # Exclude some names
    if exclude is not None:
        
        check_is_list(exclude)

        exclude = [elem.upper() for elem in exclude]

        c = ~sc.index.isin(exclude)
        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that start with ...
    if startswith is not None:
        
        check_is_list(startswith)

        startswith = [elem.upper() for elem in startswith]

        c = sc.index.str.startswith(startswith[0])
        for elem in startswith[1:]:
            c |= sc.index.str.startswith(elem)
        
        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that end with ...
    if endswith is not None:

        check_is_list(endswith)

        endswith = [elem.upper() for elem in endswith]

        c = sc.index.str.endswith(endswith[0])
        for elem in endswith[1:]:
            c |= sc.index.str.endswith(elem)

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that do not start with ...
    if not_startswith is not None:
        
        check_is_list(not_startswith)

        not_startswith = [elem.upper() for elem in not_startswith]

        c = ~sc.index.str.startswith(not_startswith[0])
        for elem in not_startswith[1:]:
            c &= ~sc.index.str.startswith(elem)
        
        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that do not end with ...
    if not_endswith is not None:

        check_is_list(not_endswith)

        not_endswith = [elem.upper() for elem in not_endswith]

        c = ~sc.index.str.endswith(not_endswith[0])
        for elem in not_endswith[1:]:
            c &= ~sc.index.str.endswith(elem)

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Name that contain ...
    if contains is not None:

        check_is_list(contains)

        contains = [elem.upper() for elem in contains]

        c = sc.index.str.contains(contains[0])
        for elem in contains[1:]:
            c |= sc.index.str.contains(elem)

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that do not contain ...
    if not_contains is not None:

        check_is_list(not_contains)

        not_contains = [elem.upper() for elem in not_contains]

        c = ~sc.index.str.contains(not_contains[0])
        for elem in not_contains[1:]:
            c &= ~sc.index.str.contains(elem)

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that have more than x characters
    if min_length is not None:

        if not isinstance(min_length, int):
            msg = ("Parameter min_length should be an integer.")
            raise TypeError(msg)

        c = (sc.index.map(len) >= min_length)

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Names that have less than x characters
    if max_length is not None:

        if not isinstance(max_length, int):
            msg = ("Parameter max_length should be an integer.")
            raise TypeError(msg)

        c = (sc.index.map(len) <= max_length)

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Composed names (contain a hyphen)
    if composed is not None:

        if not isinstance(composed, bool):
            msg = ("Parameter composed should be a boolean.")
            raise TypeError(msg)

        c = sc.index.str.contains('-')
        if not composed:
            c = ~c

        sc = sc.loc[c | (sc.index == prenom.upper())]

        if len(sc) <= 1:
            return sc

    # Return first 20 of them
    return sc.head(20)

# @lru_cache(maxsize=128)
def nombre_par_an(df, prenom):
    """Nombre de naissances ayant ce prénom chaque année."""
    c = (df['preusuel'] == prenom.upper())

    if c.sum() == 0:
        msg = ("Prénom inconnu : {}".format(prenom.capitalize()))
        raise ValueError(msg)

    dft = df.sum()

    return dft.pivot_table(values='nombre', aggfunc='sum', index='annais',
                           columns='sexe')
