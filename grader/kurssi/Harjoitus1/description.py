#!/usr/bin/python
# -*- coding: UTF-8 -*-

tests = ['test1', 'test2']
success = "Jee, hyvin meni!"
#scale = "pass"
scale= "numeric"
total_points = 5
points_required = 3
example_code = "example.py"
test1 = { "type": "compare_output",
          "name": "Testi 1",
          "description": "Tulostetaan stringi",
          "timout": 15,
          "test_results": ["Jokin meni pieleen", "expected"],
          "test_result_limits": [5, 0],
          "points": 5,
          }
test2 = { "type": "find_property",
          "name": "Testi 2",
          "description": "Onko käytetty testissä määriteltyjä mekanismeja",
          "find": ["moi","print"],
          "timout": 15,
          "test_results": ["Jokin meni pieleen", "expected"],
          "test_result_limits": [5, 0],
          "points": 5,
          }