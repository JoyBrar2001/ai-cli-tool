from agent.agent import Agent
from ui.display import print_logo

def main():
    print_logo()
    agent = Agent()

    while True:
        user_input = input("\n> ")

        if user_input.lower() == "exit":
            print("👋 Exiting...")
            break

        agent.run(user_input)

if __name__ == "__main__":
    main()