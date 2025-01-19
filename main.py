from aimo import AIMO

if __name__ == "__main__":
    ai = AIMO()
    reply = ai.get_response([{ "role": "user", "content": "I'm a bit sad today. The weather in London is really bad. It's always cloudy."}])
    print(reply)