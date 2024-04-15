from time import sleep


# LETHAL (PROTO) COM-PY-NY

def main():
    print("MOON - DESCRIPTION")
    #sleep(2)
    print("Some event")
    slow_print(input())

    action = "generic"
    print(f"You did this {action}")


def slow_print(message:str, wait:float=0.1, end:str="\n"):
    """NOTE: Only pass strings!!"""
    for char in message:
        print(char, end="", flush=True)
        sleep(wait)
    print(end=end)    

if __name__ == "__main__":
    main()