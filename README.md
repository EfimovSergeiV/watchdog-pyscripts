### Installation

###### Windows

```zsh
pip install pyaudio numpy opencv-python
.\myenv\Scripts\activate
```

###### GNU/Linux

```zsh
sudo apt install python3-pyaudio portaudio19-dev python3-all-dev
pip install pyaudio
```


###### GIT
```zsh
git update-index --assume-unchanged путь/к/файлу

git update-index --no-assume-unchanged путь/к/файлу
```


### Автозапуск Linux
```zsh
sudo nano /etc/systemd/system/myscript.service

[Unit]
Description=Мой скрипт в venv
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/myproject
ExecStart=/home/user/myproject/venv/bin/python myscript.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target


sudo systemctl daemon-reexec
sudo systemctl enable myscript.service
sudo systemctl start myscript.service


journalctl -u myscript.service -b
```