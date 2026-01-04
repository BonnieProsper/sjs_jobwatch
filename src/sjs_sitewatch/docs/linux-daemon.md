NON WINDOWS

systemd (linux, wsl, sever)
sjs-sitewatch.service

[Unit]
Description=SJS SiteWatch Alert Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python -m sjs_sitewatch.runtime.service \
  --data-dir /opt/sjs/data \
  --subscriptions /opt/sjs/subscriptions.json
Restart=always

[Install]
WantedBy=multi-user.target

TO ENABLE:

sudo systemctl enable sjs-sitewatch
sudo systemctl start sjs-sitewatch

