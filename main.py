import argparse
import generator
import checker
import split_checker

#command to start program
#python src/main.py --stage generator/checker/split


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=["generator", "checker", "split"],
        required=True
    )

    args = parser.parse_args()

    if args.stage == "generator":
        print("Generating synthetic conclusions")
        generator.main()
    
    elif args.stage == "checker":
        print("Checking synthetic conclusions")
        checker.main()
    
    elif args.stage == "split":
        print("Splitting checker results")
        split_checker.main()
        