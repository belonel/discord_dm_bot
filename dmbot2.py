from multiprocessing import Process
from bot_logic import *
from config import *
from server_logic import *
import time

def bot_run():
    client.run(DISCORD_BOT_TOKEN)

def server_run():
    print("Listening...")
    # app.run(debug=False, host='0.0.0.0', port=8085)
    port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
def server_alive():
    while(True):
        print("*server alive*")
        time.sleep(5)

if __name__ == '__main__':
    # print('hello')
    # print_all_users()
    Process(target=server_run).start()
    time.sleep(1)
    # server_run()
    # bot_run()
    Process(target=bot_run).start()
    Process(target=server_alive).start()
