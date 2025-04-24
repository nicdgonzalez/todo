import clap

app = clap.Application(
    brief="",
    after_help="Repository: https://github.com/nicdgonzalez/todo",
)

extensions = []


def main() -> None:
    """The main entry point to the program"""
    for name in extensions:
        app.extend(name=name, package="commands")

    _ = app.run()


if __name__ == "__main__":
    main()
