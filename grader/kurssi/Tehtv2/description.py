#!/usr/bin/python
# -*- coding: UTF-8 -*-

tests = ['test1', 'test2']
success = "Jee, hyvin meni!"
#scale = "pass"
#passes_required = 17
scale= "numeric"
total_points = 2
points_required = 2
#example_code = "example.py" Not used for now! Always name the example file like this

test2 = { "type": "find_property",
          "name": "Testi 2",
          "description": "Onko käytetty testissä määriteltyjä mekanismeja",
          "find": ["moi","print"],
          "timout": 15,
          "test_results": ["Jokin meni pieleen", "expected"],
          "test_result_limits": [5, 0],
          "points": 3,
          }