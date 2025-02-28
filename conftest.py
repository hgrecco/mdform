def setup_readme():
    with open("README.md") as readme, open("test_readme.txt", "w") as out:
        lines = iter(readme)
        for line in lines:
            if line.startswith("```python"):
                while not (line := next(lines)).startswith("```"):
                    if line == "time\n":
                        # Hardcoding whitespace in DataFrame output
                        # which is removed from README.md by pre-commit hooks
                        line = next(lines)
                        out.write("time")
                        out.write(" " * (len(line) - 5))
                        out.write("\n")
                    out.write(line)


setup_readme()
