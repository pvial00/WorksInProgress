
nginx:
  pkg.installed

/var/www:
  file.directory:
    - user: www-data
    - group: www-data
    - mode: 755
    - require:
      - pkg: nginx

config:
  file.managed:
    - name: /etc/nginx/sites-enabled/default
    - source: salt://webserver/default
    - user: www-data
    - group: www-data
    - mode: 644

/var/www/index.html:
  file.managed:
    - source: salt://webserver/index.html
    - user: www-data
    - group: www-data
    - mode: 644

nginxservice:
  service.running:
    - name: nginx
    - enable: True
