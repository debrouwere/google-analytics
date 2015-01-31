# encoding: utf-8

"""
Chaining for filters and segments.
"""

def condition(value):
    return "condition::" + value

def sequence(value):
    return "sequence::" + value

def all(*values):
    return condition(";".join(values))

def any(*values):
    return condition(",".join(values))

def followed_by(*values):
    return sequence(";->>".join(values))

def immediately_followed_by(*values):
    return sequence(";->".join(values))