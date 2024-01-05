from cli.main import run
from cli.args import parse_args

if __name__ == "__main__":
    args = parse_args()
    run(args)
