from attendance_ml.train import build_parser, train


if __name__ == "__main__":
    train(build_parser().parse_args())
