# main.py Entry Point for CLI runs
# imports
import sys
import os
import traceback
from predict import predict
from tokenizer import tokenize
from transformer import transform
from argparse import ArgumentParser
from utils import Spinner
#Consts
TRAINDATA = ".data/processed_data.safetensors"


def prediction_loop(local):
    print("Prediction Mode enter quit or exit to end:")
    while True:
        user_input = input("Enter text to predict: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("Exiting interactive mode.")
            break
        try:
            result = predict(user_input, local)
            print("Result: ", result)
        except Exception as e:
            print("Error while processing prediction")
            traceback.print_exc()
            sys.exit(1)

 
#local execution
def run_local(args):
    print("Running in local mode. !Execution might take some time due to training pretrained model localy!")
    if not args.data_dir:
        print("Error: data_dir argument does not exist")
        sys.exit(1)
    if not os.path.isdir(args.data_dir): 
        print(f"Error: '{args.data_dir}' is not a directory.") 
        sys.exit(1)
    
    try:
        spinner = Spinner("Tokenizing dataset")
        spinner.start()
        #tokenize
        tokenize(args.data_dir, TRAINDATA)
        
        spinner.stop()

        spinner = Spinner("Transform Model")
        spinner.start()
        # transform        
        transform(TRAINDATA)
        
        spinner.stop()
    except Exception as e:
        print(f"Error during building local transformer: {e}")
        traceback.print_exc()
        sys.exit(1)

    prediction_loop(True)

#cloud execution
def run_cloud(args):
    print("Running in cloud mode. Using already trained model. Ignoring any training data provided.")
    prediction_loop(False)

def main():
    # Arguments
    parser = ArgumentParser(description="Musk vs Trump Predictor")
    subparser = parser.add_subparsers(dest="mode")
    #local
    local_parser = subparser.add_parser("local",help="Run local model")
    local_parser.add_argument("data_dir",help="Dataset folder")
    local_parser.set_defaults(func=run_local)

    #cloud
    cloud_parser = subparser.add_parser("cloud", help="Use cloud Prediction")
    cloud_parser.set_defaults(func=run_cloud)
    # default to cloud if not provided
    parser.set_defaults(func=run_cloud)
    args = parser.parse_args()
    args.func(args)

# Main call
if __name__ == "__main__":
    main()
