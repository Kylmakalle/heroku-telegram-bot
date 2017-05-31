# Hosting telegram bot on [Heroku](https://heroku.com) for free.
Easy way to host your python telegram bot on Heroku

## Deploying via [Heroku Toolbelt](https://toolbelt.heroku.com/) (CLI)
Install [Heroku Toolbelt](https://toolbelt.heroku.com/), then:
### Clone repository
`git clone https://github.com/Kylmakalle/heroku-telegram-bot.git`
### Edit files
1. Edit [bot.py](https://github.com/Kylmakalle/heroku-telegram-bot/blob/master/bot.py) file with your code

    1. **ATTENTION!** Do not collapse/delete/comment `some_token = os.environ[SOME_TOKEN]` style stings _(you can delete redis setup line if you do not need it)_, **do not change them with your REAL tokens**, all tokens will be setted up below in this guide!
    
    2. [More About Config Vars](https://devcenter.heroku.com/articles/config-vars)
    3. Also, don't do like [this](http://i.imgur.com/Yni1jZX.png), it's insecure, **realy.**


2. Edit [requirments.txt](https://github.com/Kylmakalle/heroku-telegram-bot/blob/master/requirements.txt) with your code's dependencies
3. Specify your python [runtime](https://github.com/Kylmakalle/heroku-telegram-bot/blob/master/runtime.txt), avaliable versions listed [here](https://devcenter.heroku.com/articles/python-runtimes)

### Go to command line
```
cd heroku-telegram-bot
heroku login
heroku create --region eu appname # create app in eu region, common regions: eu, us
heroku addons:create heroku-redis:hobby-dev -a appname # (Optionaly) installing redis
heroku buildpacks:set heroku/python # set python buildpack
git push heroku master # deploy app to heroku
heroku config:set TELEGRAM_TOKEN=123456789:AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLL # set config vars, insert your own
heroku config:set SOME_API_TOKEN=qwertyuiop1234567890
                ...
heroku ps:scale bot=1 # start bot dyno
heroku logs --tail # If for some reason it’s not working, check the logs
heroku ps:stop bot #stop bot dyno
```

## Deploying via [Heroku Dashboard](https://dashboard.heroku.com) (GUI)
1. [Fork](https://github.com/Kylmakalle/heroku-telegram-bot/fork) this repo to your account. 
2. [Edit files](https://github.com/Kylmakalle/heroku-telegram-bot#edit-files)
3. Go to [Dashboard](https://dashboard.heroku.com), login, Press _New_ and choose _Create new app._
4. Fill in an _App Name_ and choose _Runtime Region._
5. Connect your GitHub repo at _Deploy_ page.
6. Setup **Automatics deploys** _(Optionaly)._
7. _Deploy a GitHub branch._
8. Then go to a _Settings_ page, click _Reveal Config Vars_ and then add your own, for example:
![Config Vars](http://i.imgur.com/C3cmphh.png)
9. **Finally**, go to the _Resources_ page.
    1. Install _Heroku Redis_ add-on _(Optionaly)_
    2. Press on a small pen button, move slider and then click _Confirm_, that will start bot dyno.
    3. Simply move slider back if you need to stop bot dyno, remember to click _Confirm_.
    4. If for some reason it’s not working, check the logs here 
    
    ![Logs](http://i.imgur.com/rIHU6zF.png)

### More about
- https://devcenter.heroku.com/articles/dynos
- https://devcenter.heroku.com/articles/config-vars
- https://devcenter.heroku.com/articles/heroku-redis
- https://devcenter.heroku.com/articles/error-codes

Thanks to [Roman Zaynetdinov](https://github.com/zaynetro) for awesome and easy CLI guide.
