tests = ['test1']
success = "Jee, hyvin meni!"
total_points = 5
points_required = 5
example_code = "example.py"
test1 = { "type": "compare_output",
          "description": "Tulostetaan stringi",
          "test": "diff_test()",
          "timout": 15,
          "test_results": ["Jokin meni pieleen", "expected"],
          "test_result_limits": [5, 0],
          "points": 5,
          }
