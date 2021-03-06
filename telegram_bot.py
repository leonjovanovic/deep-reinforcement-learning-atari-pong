import time
from telegram import Bot
import datetime

def telegram_send(message):
    chat_id = "CHAT_ID"
    token = "TOKEN_ID"
    bot = Bot(token=token)
    bot.send_message(chat_id=chat_id, text=message)

def welcome_msg(multi_step, double_dqn, dueling):
    st = 'Hi! Starting learning with DQN Multi-step = %d, Double DQN = %r, Dueling DQN = %r' % (multi_step, double_dqn, dueling)
    telegram_send(st)
    
def info_msg(iteration, max_iteration, mean_reward, loss):
    st = 'Iteration %d/%d  Mean reward: %.2f Loss: %.4f' % (iteration, max_iteration, mean_reward, loss)
    telegram_send(st)

def end_msg(learning_time):
    st = 'Finished! Learning time: ' + str(datetime.timedelta(seconds=int(learning_time)))
    telegram_send(st)
    print(st)


# https://api.telegram.org/botTOKEN_ID/getUpdates
