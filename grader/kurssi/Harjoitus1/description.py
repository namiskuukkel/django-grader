#!/usr/bin/python
# -*- coding: UTF-8 -*-

tests = ['test1']
success = "Jee, hyvin meni!"
total_points = 5
points_required = 5
example_code = "example.py"
test1 = { "type": "compare_output",
          "name": "Testi 1",
          "description": "Tulostetaan stringi",
          "timout": 15,
          "test_results": ["Jokin meni pieleen", "expected"],
          "test_result_limits": [5, 0],
          "points": 5,
          }
test2 = { "type": "inject_variables",
          "name": "Testi 1",
          "description": "Tulostetaan stringi",
          "test": "test.py",
          "timout": 15,
          "test_results": ["Jokin meni pieleen", "expected"],
          "test_result_limits": [5, 0],
          "points": 5,
          }