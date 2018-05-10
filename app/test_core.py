# coding: utf8
import numpy as np

import pandas as pd

import prenoms

print("--> Reading first names file from 1900 to 2015 (takes time).")
df = prenoms.read_prenom_file('assets/dpt2016.txt')
print("--> Done!")

def valid_response(response):
    """Basic testing on responses"""
    assert isinstance(response, pd.Series)

    assert len(response) <= 20

    assert response.index.dtype == 'O'

    assert response.dtype == np.float64

    assert all([(elem >= 0) and (elem <= 1) for elem in response])

print("--> Basic male name, no options...")
response = prenoms.score_filter(df, "Pierre")
print(response)
valid_response(response)
print("--> ok!")

print("--> Basic female name, no options...")
response = prenoms.score_filter(df, "Mona")
valid_response(response)
print("--> ok!")

print("--> Unknown name, no options...")
try:
    prenoms.score_filter(df, "Trouduc")
except Exception as e:
    print("--> ok! (raised {})".format(repr(e)))

print("--> Male name asking for a female name, no options...")
response = prenoms.score_filter(df, "Pierre", 'F')
valid_response(response)
print("--> ok!")

print("--> Female name asking for a male name, no options...")
response = prenoms.score_filter(df, "Mona", 'M')
valid_response(response)
print("--> ok!")

print("--> Checking exclude...")
response = prenoms.score_filter(df, "Pierre", "M")
prenom = response.index[1]
response = prenoms.score_filter(df, "Pierre", "M", exclude=[prenom])
try:
    valid_response(response)
    assert (response.index[1:] != prenom).all()
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking startswith...")
response = prenoms.score_filter(df, "Pierre", "M", startswith=['J', 'L'])
try:
    valid_response(response)
    assert all([elem[0] in ['J', 'L'] for elem in response.index[1:]])
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking endswith...")
response = prenoms.score_filter(df, "Pierre", "M", endswith=['N', 'S'])
try:
    valid_response(response)
    assert all([elem[-1] in ['N', 'S'] for elem in response.index[1:]])
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking not_startswith...")
response = prenoms.score_filter(df, "Pierre", "M", not_startswith=['J', 'L'])
try:
    valid_response(response)
    assert all([elem[0] not in ['J', 'L'] for elem in response.index[1:]])
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking not_endswith...")
response = prenoms.score_filter(df, "Pierre", "M", not_endswith=['N', 'S'])
try:
    valid_response(response)
    assert all([elem[-1] not in ['N', 'S'] for elem in response.index[1:]])
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking contains...")
response = prenoms.score_filter(df, "Pierre", "M", contains=['Ç', 'É'])
try:
    valid_response(response)
    assert response.index[1:].str.contains('Ç|É').all()
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking not_contains...")
response = prenoms.score_filter(df, "Pierre", "M", not_contains=['Ç', 'É'])
try:
    valid_response(response)
    assert ~response.index[1:].str.contains('Ç|É').any()
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking min_length...")
response = prenoms.score_filter(df, "Pierre", "M", min_length=5)
try:
    valid_response(response)
    assert response.index[1:].map(len).min() >= 5
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking max_length...")
response = prenoms.score_filter(df, "Pierre", "M", max_length=5)
try:
    valid_response(response)
    assert response.index[1:].map(len).max() <= 5
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking composed...")
response = prenoms.score_filter(df, "Pierre", "M", composed=True)
try:
    valid_response(response)
    assert response.index[1:].str.contains('-').all()
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> Checking not composed...")
response = prenoms.score_filter(df, "Pierre", "M", composed=False)
try:
    valid_response(response)
    assert ~response.index[1:].str.contains('-').any()
except AssertionError:
    print(response)
    raise
print("--> ok!")

print("--> All options!!!")
response = prenoms.score_filter(df, "Pierre", 'F', exclude=["Jeanne"],
                                startswith=['F', 'C'], endswith=['E', 'A'],
                                not_startswith=['X', 'L'],
                                not_endswith=['O', 'I'], contains=['S', 'T'],
                                not_contains=['Z', 'U'], min_length=1,
                                max_length=10, composed=False)
print(response)
valid_response(response)
print("--> ok!")
